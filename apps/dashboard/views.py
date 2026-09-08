"""Dashboard views providing aggregated weather analytics summaries."""
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.http import JsonResponse
from core.models import IncidentReport

@method_decorator(csrf_exempt, name='dispatch')
class IncidentReportView(View):
    """Handle incident report submissions via POST and return precautions."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    # Hardcoded precaution messages per category
    PRECAUTIONS = {
        "flood": [
            "Move to higher ground immediately.",
            "Secure important documents and valuables.",
            "Stay away from flowing water and avoid driving through flooded areas."
        ],
        "fire": [
            "Evacuate the area following official routes.",
            "Cover your mouth to avoid inhaling smoke.",
            "Do not attempt to extinguish large fires yourself."
        ],
        "storm": [
            "Stay indoors and away from windows.",
            "Secure loose outdoor objects.",
            "Monitor local weather alerts for updates."
        ],
        "lightning": [
            "Seek shelter inside a building or vehicle.",
            "Avoid using wired electronics and stay away from water.",
            "Wait at least 30 minutes after the last lightning strike before resuming outdoor activities."
        ],
        "heatwave": [
            "Stay hydrated and limit outdoor activities.",
            "Use fans or air conditioning if possible.",
            "Check on vulnerable neighbors and family members."
        ],
    }

    def post(self, request: Request) -> JsonResponse:
        """Process incident report JSON payload.

        Expected JSON structure:
        {
            "description": "...",
            "lat": 12.9716,
            "lon": 77.5946
        }
        """
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        description = data.get("description", "").strip()
        lat = data.get("lat")
        lon = data.get("lon")

        # Validate required fields
        if not description or lat is None or lon is None:
            return JsonResponse({"error": "Missing description, latitude, or longitude."}, status=400)

        # Validate coordinate ranges
        try:
            lat = float(lat)
            lon = float(lon)
        except (TypeError, ValueError):
            return JsonResponse({"error": "Latitude and longitude must be numeric."}, status=400)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return JsonResponse({"error": "Latitude or longitude out of valid range."}, status=400)

        # Keyword matching for categories
        description_lower = description.lower()
        matched_category = None
        for category in self.PRECAUTIONS.keys():
            if category in description_lower:
                matched_category = category
                break
        if not matched_category:
            matched_category = "general"
            precautions = ["Stay safe and follow local authority guidance."]
        else:
            precautions = self.PRECAUTIONS[matched_category]

        # Save incident report
        IncidentReport.objects.create(
            description=description,
            category=matched_category,
            lat=lat,
            lon=lon,
        )

        return JsonResponse({
            "category": matched_category,
            "precautions": precautions,
        }, status=200)

    def get(self, request: Request) -> JsonResponse:
        """Return a simple description for GET requests (optional)."""
        return JsonResponse({"detail": "Incident report endpoint. Submit POST with description, lat, lon."})



class IncidentListView(APIView):
    """Return recent incident reports for map pins."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request: Request) -> JsonResponse:
        reports = IncidentReport.objects.all().order_by('-created_at')[:20]
        data = [
            {
                "id": r.id,
                "category": r.category,
                "lat": r.lat,
                "lon": r.lon,
                "description": r.description,
            }
            for r in reports
        ]
        return JsonResponse({"incidents": data})

    """Endpoint for incident data used by the dashboard."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request: Request) -> Response:
        """Return JSON list of recent incidents."""
        from apps.incidents.models import Incident
        now = timezone.now()
        recent = Incident.objects.filter(created_at__gte=now - timezone.timedelta(days=7)).order_by('-created_at')[:10]
        data = [{
            "id": inc.id,
            "severity": inc.severity,
            "status": inc.status,
            "started": inc.start_time,
        } for inc in recent]
        return Response({"incidents": data})

class IncidentMapView(View):
    """Placeholder map view for incidents."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request: Request) -> Response:
        return render(request, "incident_map.html")

class DashboardSummaryView(APIView):
    """Return a high-level summary of platform data for the dashboard home."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request: Request) -> Response:
        """GET /api/dashboard/summary/

        Returns:
            JSON payload with counts and latest statistics across all apps.
        """
        from apps.alerts.models import AlertEvent, AlertRule
        from apps.incidents.models import Incident
        from apps.weather.models import WeatherObservation, WeatherStation

        now = timezone.now()
        last_24h = now - timezone.timedelta(hours=24)

        # Station statistics
        station_stats = WeatherStation.objects.aggregate(
            total=Count("id"),
            active=Count("id", filter=models_filter(is_active=True)),
        )

        # Recent observation statistics (last 24 h)
        obs_stats = WeatherObservation.objects.filter(
            timestamp__gte=last_24h
        ).aggregate(
            count=Count("id"),
            avg_temp=Avg("temperature_c"),
            max_temp=Max("temperature_c"),
            min_temp=Min("temperature_c"),
            avg_humidity=Avg("humidity_pct"),
            total_precip=Avg("precipitation_mm"),
        )

        # Active incidents
        incident_stats = Incident.objects.filter(
            status__in=[Incident.Status.OPEN, Incident.Status.MONITORING]
        ).aggregate(
            total_active=Count("id"),
            critical=Count("id", filter=models_filter(severity=Incident.Severity.CRITICAL)),
            high=Count("id", filter=models_filter(severity=Incident.Severity.HIGH)),
        )

        # Alert events in last 24 h
        alert_stats = AlertEvent.objects.filter(
            triggered_at__gte=last_24h
        ).aggregate(
            total=Count("id"),
            pending=Count("id", filter=models_filter(notify_status=AlertEvent.NotifyStatus.PENDING)),
            sent=Count("id", filter=models_filter(notify_status=AlertEvent.NotifyStatus.SENT)),
            failed=Count("id", filter=models_filter(notify_status=AlertEvent.NotifyStatus.FAILED)),
        )

        return Response(
            {
                "generated_at": now.isoformat(),
                "stations": station_stats,
                "observations_last_24h": obs_stats,
                "active_incidents": incident_stats,
                "alert_events_last_24h": alert_stats,
                "active_alert_rules": AlertRule.objects.filter(is_active=True).count(),
            }
        )


def models_filter(**kwargs):
    """Helper to build a Q-object filter for use inside aggregate()."""
    from django.db.models import Q

    return Q(**kwargs)


from django.shortcuts import render


def home_view(request):
    """Render the professional Weather Analytics Dashboard homepage."""
    from apps.alerts.models import AlertEvent, AlertRule
    from apps.incidents.models import Incident
    from apps.weather.models import WeatherObservation, WeatherStation

    now = timezone.now()
    last_24h = now - timezone.timedelta(hours=24)

    total_stations = WeatherStation.objects.count()
    active_stations = WeatherStation.objects.filter(is_active=True).count()

    recent_obs = WeatherObservation.objects.select_related("station").order_by("-timestamp")[:10]

    obs_24h = WeatherObservation.objects.filter(timestamp__gte=last_24h)
    avg_temp = obs_24h.aggregate(Avg("temperature_c"))["temperature_c__avg"]
    max_temp = obs_24h.aggregate(Max("temperature_c"))["temperature_c__max"]
    min_temp = obs_24h.aggregate(Min("temperature_c"))["temperature_c__min"]
    obs_count = obs_24h.count()

    incidents_qs = Incident.objects.filter(
        status__in=[Incident.Status.OPEN, Incident.Status.MONITORING]
    )
    critical_incidents_count = incidents_qs.filter(severity=Incident.Severity.CRITICAL).count()
    active_incidents = incidents_qs.order_by("-start_time")[:6]


    alert_events = AlertEvent.objects.order_by("-triggered_at")[:6]
    active_rules_count = AlertRule.objects.filter(is_active=True).count()

    stations = WeatherStation.objects.filter(is_active=True)[:8]

    demo_cities = [
        {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "state": "Karnataka"},
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "state": "Maharashtra"},
        {"name": "Delhi", "lat": 28.6139, "lon": 77.2090, "state": "NCT"},
        {"name": "Chennai", "lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu"},
    ]

    context = {
        "generated_at": now,
        "total_stations": total_stations,
        "active_stations": active_stations,
        "obs_count": obs_count,
        "avg_temp": round(avg_temp, 1) if avg_temp is not None else 21.4,
        "max_temp": round(max_temp, 1) if max_temp is not None else 28.5,
        "min_temp": round(min_temp, 1) if min_temp is not None else 14.2,
        "active_incidents": active_incidents,
        "critical_incidents_count": critical_incidents_count,
        "recent_observations": recent_obs,
        "alert_events": alert_events,
        "active_rules_count": active_rules_count,
        "stations": stations,
        "demo_cities": demo_cities,
    }
    return render(request, "home.html", context)

# New static page views
from django.shortcuts import render

def dashboard_page(request):
    """Render the main dashboard page (new template)."""
    return render(request, "dashboard.html")

def cities_page(request):
    """Render the 4 Demo Cities page."""
    return render(request, "cities.html")

def forecast_page(request):
    """Render the 5‑Day Forecast page."""
    return render(request, "forecast.html")

def prediction_page(request):
    """Render the Prediction Line Graph page."""
    return render(request, "prediction.html")

def alerts_page(request):
    """Render the Weather Alerts page."""
    return render(request, "alerts.html")

def weather_page(request):
    """Render the Weather page."""
    return render(request, "weather.html")

def incidents_page(request):
    """Render the Citizen Reports & Incidents page."""
    return render(request, "incidents.html")

def assistant_page(request):
    """Render the AI Assistant page."""
    return render(request, "assistant.html")

def historical_page(request):
    """Render the Historical Weather Analytics page."""
    return render(request, "historical.html")


# ── User Authentication & Profile Views ───────────────────────
import csv
import os
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from core.models import UserPreference, IncidentReport


def login_view(request):
    """Handle user Sign In and Credential Storage (Registration). Always renders the login page."""
    if request.GET.get("logout") or request.GET.get("reset"):
        logout(request)

    tab = request.GET.get("tab", "store")
    error = None
    prefill_email = ""

    if request.method == "POST":
        action = request.POST.get("action", "login")

        if action in ("register", "store"):
            # Credential Storage / Account Registration
            email = request.POST.get("email", "").strip()
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "").strip()
            password_confirm = request.POST.get("password_confirm", "").strip() or password
            home_city = request.POST.get("home_city", "Bengaluru").strip() or "Bengaluru"
            prefill_email = email

            if not email or not password:
                error = "Email address and password are required to store your credentials."
                tab = "store"
            elif "@" not in email or "." not in email:
                error = "Please enter a valid email address (e.g., user@domain.com)."
                tab = "store"
            elif len(password) < 4:
                error = "Password must be at least 4 characters long."
                tab = "store"
            elif password != password_confirm:
                error = "Passwords do not match. Please re-enter identical passwords."
                tab = "store"
            elif User.objects.filter(email__iexact=email).exists():
                error = f"The email '{email}' is already registered! Please sign in with your stored password."
                tab = "login"
            else:
                if not username:
                    username = email.split("@")[0].replace("+", "_").replace(".", "_")
                final_username = username
                if User.objects.filter(username__iexact=final_username).exists():
                    import random
                    final_username = f"{username}_{random.randint(100, 999)}"

                user = User.objects.create_user(
                    username=final_username,
                    email=email,
                    password=password,
                )
                UserPreference.objects.create(
                    user=user,
                    home_city=home_city,
                    favorite_cities=[{"name": home_city, "state": "Monitored Corridor"}],
                )
                login(request, user)
                return redirect("/dashboard/?stored=true")

        else:
            # Sign In with Stored Credentials
            login_input = (request.POST.get("email") or request.POST.get("username") or "").strip()
            password = request.POST.get("password", "").strip()
            prefill_email = login_input

            username_to_auth = login_input
            if "@" in login_input:
                user_by_email = User.objects.filter(email__iexact=login_input).first()
                if user_by_email:
                    username_to_auth = user_by_email.username
                else:
                    error = f"No account found with email '{login_input}'. Please store your email and password first."
                    tab = "store"
                    return render(request, "login.html", {
                        "error": error,
                        "tab": tab,
                        "prefill_email": prefill_email,
                    })

            user = authenticate(request, username=username_to_auth, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get("next") or "/dashboard/"
                return redirect(next_url)
            else:
                error = "Invalid password or email. Please check your credentials."
                tab = "login"

    return render(request, "login.html", {
        "error": error,
        "tab": tab,
        "prefill_email": prefill_email,
    })


def register_view(request):
    """Entry point for direct registration / credential storage."""
    if request.user.is_authenticated:
        return redirect("/dashboard/")
    if request.method == "POST":
        post_data = request.POST.copy()
        post_data["action"] = "register"
        request.POST = post_data
        return login_view(request)
    return redirect("/?tab=store")


def logout_view(request):
    """Handle user Sign Out."""
    logout(request)
    return redirect("/")



@login_required(login_url="/")
def profile_view(request):
    """User profile and stored weather preferences."""
    pref, _ = UserPreference.objects.get_or_create(user=request.user)
    user_incidents = IncidentReport.objects.filter(author=request.user.username)
    return render(request, "profile.html", {
        "pref": pref,
        "favorite_cities": pref.favorite_cities or [],
        "user_incidents": user_incidents,
    })


# ── Historical Weather & Dataset Analytics ────────────────────
_DATASET_CACHE = {}


def load_climate_dataset():
    """Load and parse Indian_Climate_Dataset_2024_2025.csv with caching."""
    global _DATASET_CACHE
    if "climate" in _DATASET_CACHE:
        return _DATASET_CACHE["climate"]

    csv_path = os.path.join(settings.BASE_DIR, "data", "Indian_Climate_Dataset_2024_2025.csv")
    records = []
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    records.append({
                        "date": r.get("Date"),
                        "city": r.get("City"),
                        "state": r.get("State"),
                        "max_temp": float(r.get("Temperature_Max (°C)") or r.get("Temperature_Max (C)") or 0),
                        "min_temp": float(r.get("Temperature_Min (°C)") or r.get("Temperature_Min (C)") or 0),
                        "avg_temp": float(r.get("Temperature_Avg (°C)") or r.get("Temperature_Avg (C)") or 0),
                        "humidity": float(r.get("Humidity (%)") or 0),
                        "rainfall": float(r.get("Rainfall (mm)") or 0),
                        "wind": float(r.get("Wind_Speed (km/h)") or 0),
                        "aqi": r.get("AQI"),
                    })
                except Exception:
                    continue
    _DATASET_CACHE["climate"] = records
    return records


def load_century_dataset():
    """Load and parse Weather_Data_India_1901_2017.csv with caching."""
    global _DATASET_CACHE
    if "century" in _DATASET_CACHE:
        return _DATASET_CACHE["century"]

    csv_path = os.path.join(settings.BASE_DIR, "data", "Weather_Data_India_1901_2017.csv")
    records = []
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    records.append({
                        "year": r.get("YEAR"),
                        "jan_temp": float(r.get("JAN") or 0),
                        "max_temp": float(r.get("MAY") or 0),
                        "min_temp": float(r.get("DEC") or 0),
                    })
                except Exception:
                    continue
    _DATASET_CACHE["century"] = records
    return records


CITY_COORDINATES = {
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
}


def get_live_weather_telemetry(city_name="Bengaluru"):
    """Fetch live weather metrics and 12-point diurnal temperature curve."""
    lat, lon = CITY_COORDINATES.get(str(city_name).lower().strip(), (12.9716, 77.5946))
    current_temp = 25.0
    live_curve = []
    try:
        from core.views import fetch_open_meteo_forecast
        data = fetch_open_meteo_forecast(lat, lon)
        current = data.get("current", {})
        if "temperature_2m" in current and current["temperature_2m"] is not None:
            current_temp = round(float(current["temperature_2m"]), 1)

        hourly = data.get("hourly", {}).get("temperature_2m", [])
        if len(hourly) >= 24:
            live_curve = [round(float(hourly[i]), 1) for i in range(0, 24, 2)]
    except Exception:
        pass

    if not live_curve:
        live_curve = [
            round(current_temp - 3.5, 1), round(current_temp - 4.2, 1), round(current_temp - 5.0, 1),
            round(current_temp - 4.0, 1), round(current_temp - 2.0, 1), round(current_temp + 1.5, 1),
            round(current_temp + 4.0, 1), round(current_temp + 5.2, 1), round(current_temp + 4.5, 1),
            round(current_temp + 2.8, 1), round(current_temp + 0.5, 1), round(current_temp - 1.8, 1)
        ]

    return {
        "current_temp": current_temp,
        "live_curve": live_curve,
    }


def normalize_record_dict(raw):
    """Normalize arbitrary CSV or JSON dictionary into clean weather observation."""
    norm = {}
    for k, v in raw.items():
        if k is None or v is None:
            continue
        cleaned_key = "".join(ch for ch in str(k).lower() if ch.isalnum())
        norm[cleaned_key] = str(v).strip()

    date_val = None
    for dk in ["date", "year", "timestamp", "time", "day", "datetime"]:
        if dk in norm and norm[dk]:
            date_val = norm[dk]
            break
    if not date_val:
        date_val = "2024-01-01"

    city_val = None
    for ck in ["city", "location", "town", "station", "stationname", "place"]:
        if ck in norm and norm[ck]:
            city_val = norm[ck]
            break
    if not city_val:
        city_val = "Uploaded Data"

    def parse_flt(val_keys, default=None):
        for vk in val_keys:
            if vk in norm and norm[vk] != "":
                try:
                    cleaned = "".join(c for c in norm[vk] if c.isdigit() or c in ".-")
                    if cleaned:
                        return round(float(cleaned), 1)
                except Exception:
                    pass
        return default

    max_t = parse_flt(["temperaturemaxc", "temperaturemax", "maxc", "maxtemp", "max", "tmax", "high", "may", "tempmax"])
    min_t = parse_flt(["temperatureminc", "temperaturemin", "minc", "mintemp", "min", "tmin", "low", "dec", "tempmin"])
    avg_t = parse_flt(["temperatureavgc", "temperatureavg", "avgtemp", "mean", "meantemp", "avg", "temp", "temperature", "tavg"])
    rain_val = parse_flt(["rainfallmm", "rainfall", "rain", "precipitation", "precip"], default=0.0)
    humidity_val = parse_flt(["humidity", "relhumidity", "relativehumidity", "rh"], default=60.0)
    wind_val = parse_flt(["windspeedkmh", "windspeed", "wind"], default=12.0)

    aqi_val = "Good"
    for ak in ["aqi", "airquality", "airqualityindex"]:
        if ak in norm and norm[ak]:
            aqi_val = norm[ak]
            break

    if avg_t is None:
        if max_t is not None and min_t is not None:
            avg_t = round((max_t + min_t) / 2.0, 1)
        elif max_t is not None:
            avg_t = round(max_t - 2.5, 1)
        elif min_t is not None:
            avg_t = round(min_t + 2.5, 1)
        else:
            avg_t = 25.0

    if max_t is None:
        max_t = round(avg_t + 3.0, 1)
    if min_t is None:
        min_t = round(avg_t - 3.0, 1)

    return {
        "date": date_val,
        "city": city_val,
        "max_temp": max_t,
        "min_temp": min_t,
        "avg_temp": avg_t,
        "rainfall": rain_val or 0.0,
        "humidity": humidity_val or 60.0,
        "wind": wind_val or 10.0,
        "aqi": aqi_val,
    }


def parse_custom_weather_file(uploaded_file, filename):
    """Parse CSV or JSON uploaded weather datasets into normalized records."""
    records = []
    content = uploaded_file.read().decode("utf-8", errors="ignore")

    if filename.lower().endswith(".json"):
        try:
            raw_data = json.loads(content)
            if isinstance(raw_data, dict):
                raw_records = raw_data.get("records") or raw_data.get("data") or [raw_data]
            elif isinstance(raw_data, list):
                raw_records = raw_data
            else:
                raw_records = []
            for r in raw_records:
                if isinstance(r, dict):
                    records.append(normalize_record_dict(r))
        except Exception:
            pass
    else:
        lines = content.splitlines()
        reader = csv.DictReader(lines)
        for r in reader:
            rec = normalize_record_dict(r)
            if rec:
                records.append(rec)

    return records


def api_historical_weather(request):
    """API returning historical metrics, comparative telemetry, and observations."""
    city = request.GET.get("city", "Bengaluru").strip()
    mode = request.GET.get("mode", "recent")

    # Get live telemetry for comparative evaluation
    live_telemetry = get_live_weather_telemetry(city)
    current_temp = live_telemetry["current_temp"]
    live_curve = live_telemetry["live_curve"]

    if mode == "custom":
        custom_recs = _DATASET_CACHE.get("custom") or request.session.get("custom_dataset") or []
        if not custom_recs:
            custom_recs = load_climate_dataset()

        city_recs = [r for r in custom_recs if r.get("city", "").lower() == city.lower()]
        recs = city_recs if city_recs else custom_recs

        temps = [r["avg_temp"] for r in recs if r.get("avg_temp") is not None and r.get("avg_temp") > 0]
        mean_t = round(sum(temps) / len(temps), 1) if temps else 25.0
        max_t = round(max([r.get("max_temp", mean_t) for r in recs]), 1) if recs else 35.0
        min_t = round(min([r.get("min_temp", mean_t) for r in recs if r.get("min_temp") is not None]), 1) if recs else 15.0
        total_rain = round(sum([r.get("rainfall", 0) or 0 for r in recs]), 1)

        hist_curve = [
            round(mean_t - 3.5, 1), round(mean_t - 4.2, 1), round(mean_t - 5.0, 1),
            round(mean_t - 4.0, 1), round(mean_t - 2.0, 1), round(mean_t + 1.5, 1),
            round(mean_t + 4.0, 1), round(mean_t + 5.2, 1), round(mean_t + 4.5, 1),
            round(mean_t + 2.8, 1), round(mean_t + 0.5, 1), round(mean_t - 1.8, 1)
        ]

        temp_diff = round(current_temp - mean_t, 1)
        diff_str = f"+{temp_diff}" if temp_diff > 0 else str(temp_diff)
        anomaly_status = f"{diff_str}°C vs Ingested Dataset Mean"

        return JsonResponse({
            "city": f"{city} (Ingested Dataset)",
            "mean_temp": mean_t,
            "max_temp": max_t,
            "min_temp": min_t,
            "total_rain": total_rain,
            "current_temp": current_temp,
            "temp_anomaly": temp_diff,
            "anomaly_status": anomaly_status,
            "records": recs[:60],
            "live_curve": live_curve,
            "hist_curve": hist_curve,
        })
    elif mode == "century":
        data = load_century_dataset()
        temps = [r["max_temp"] for r in data if r["max_temp"] > 0]
        mean_t = round(sum(temps) / len(temps), 1) if temps else 28.5
        max_t = max(temps) if temps else 34.0
        min_t = min([r["min_temp"] for r in data if r["min_temp"] > 0]) if data else 18.0

        hist_curve = [22, 21, 20, 20, 22, 25, 28, 30, 29, 27, 25, 23]
        temp_diff = round(current_temp - mean_t, 1)
        diff_str = f"+{temp_diff}" if temp_diff > 0 else str(temp_diff)

        return JsonResponse({
            "city": "All-India Century Baseline",
            "mean_temp": mean_t,
            "max_temp": max_t,
            "min_temp": min_t,
            "total_rain": 1180,
            "current_temp": current_temp,
            "temp_anomaly": temp_diff,
            "anomaly_status": f"{diff_str}°C vs Century Baseline",
            "records": data[:60],
            "live_curve": live_curve,
            "hist_curve": hist_curve,
        })
    else:
        all_recs = load_climate_dataset()
        city_recs = [r for r in all_recs if r["city"].lower() == city.lower()]
        recs = city_recs if city_recs else all_recs[:100]

        temps = [r["avg_temp"] for r in recs if r["avg_temp"] > 0]
        mean_t = round(sum(temps) / len(temps), 1) if temps else 26.2
        max_t = max([r["max_temp"] for r in recs]) if recs else 36.5
        min_t = min([r["min_temp"] for r in recs if r["min_temp"] > 0]) if recs else 16.0
        total_rain = round(sum([r["rainfall"] for r in recs]), 1) if recs else 420.0

        hist_curve = [
            round(mean_t - 3.5, 1), round(mean_t - 4.2, 1), round(mean_t - 5.0, 1),
            round(mean_t - 4.0, 1), round(mean_t - 2.0, 1), round(mean_t + 1.5, 1),
            round(mean_t + 4.0, 1), round(mean_t + 5.2, 1), round(mean_t + 4.5, 1),
            round(mean_t + 2.8, 1), round(mean_t + 0.5, 1), round(mean_t - 1.8, 1)
        ]

        temp_diff = round(current_temp - mean_t, 1)
        diff_str = f"+{temp_diff}" if temp_diff > 0 else str(temp_diff)

        return JsonResponse({
            "city": city,
            "mean_temp": mean_t,
            "max_temp": max_t,
            "min_temp": min_t,
            "total_rain": total_rain,
            "current_temp": current_temp,
            "temp_anomaly": temp_diff,
            "anomaly_status": f"{diff_str}°C vs 2024–2025 Baseline",
            "records": recs[:60],
            "live_curve": live_curve,
            "hist_curve": hist_curve,
        })


@csrf_exempt
def api_save_favorite(request):
    """Save or remove favorite city for authenticated user."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required"}, status=401)

    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else request.POST
        action = data.get("action", "add")
        city_name = data.get("city", "").strip()

        pref, _ = UserPreference.objects.get_or_create(user=request.user)
        favs = pref.favorite_cities or []

        if action == "add":
            if not any(f.get("name", "").lower() == city_name.lower() for f in favs):
                favs.append({"name": city_name, "state": "Monitored"})
                pref.favorite_cities = favs
                pref.save()
        elif action == "remove":
            pref.favorite_cities = [f for f in favs if f.get("name", "").lower() != city_name.lower()]
            pref.save()

        return JsonResponse({"status": "success", "favorites": pref.favorite_cities})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)


@csrf_exempt
def api_dataset_upload(request):
    """Ingest user-uploaded CSV/JSON dataset and immediately compare with live telemetry."""
    if request.method != "POST" or "dataset" not in request.FILES:
        return JsonResponse({"error": "No dataset file uploaded"}, status=400)

    try:
        uploaded_file = request.FILES["dataset"]
        records = parse_custom_weather_file(uploaded_file, uploaded_file.name)
        if not records:
            return JsonResponse({"error": "Could not parse valid weather rows from the uploaded file"}, status=400)

        # Cache parsed dataset in memory and session
        _DATASET_CACHE["custom"] = records
        _DATASET_CACHE["custom_filename"] = uploaded_file.name
        request.session["custom_dataset"] = records[:300]
        request.session["custom_filename"] = uploaded_file.name

        # Identify cities in the dataset
        cities = list(dict.fromkeys([r["city"] for r in records if r.get("city") and r["city"] != "Uploaded Data"]))
        primary_city = cities[0] if cities else "Bengaluru"

        # Compute summary statistics
        temps = [r["avg_temp"] for r in records if r.get("avg_temp") is not None and r.get("avg_temp") > 0]
        mean_t = round(sum(temps) / len(temps), 1) if temps else 25.0
        max_t = round(max([r.get("max_temp", mean_t) for r in records]), 1)
        min_t = round(min([r.get("min_temp", mean_t) for r in records if r.get("min_temp") is not None]), 1)
        total_rain = round(sum([r.get("rainfall", 0) or 0 for r in records]), 1)

        # Fetch Live Current Telemetry for Comparison
        live_telemetry = get_live_weather_telemetry(primary_city)
        current_temp = live_telemetry["current_temp"]
        live_curve = live_telemetry["live_curve"]

        # Diurnal curve representing the ingested dataset
        hist_curve = [
            round(mean_t - 3.5, 1), round(mean_t - 4.2, 1), round(mean_t - 5.0, 1),
            round(mean_t - 4.0, 1), round(mean_t - 2.0, 1), round(mean_t + 1.5, 1),
            round(mean_t + 4.0, 1), round(mean_t + 5.2, 1), round(mean_t + 4.5, 1),
            round(mean_t + 2.8, 1), round(mean_t + 0.5, 1), round(mean_t - 1.8, 1)
        ]

        temp_diff = round(current_temp - mean_t, 1)
        diff_str = f"+{temp_diff}" if temp_diff > 0 else str(temp_diff)
        if temp_diff > 0.5:
            anomaly_status = f"{diff_str}°C Warmer than Ingested Historical Baseline"
            status_color = "var(--rose)"
        elif temp_diff < -0.5:
            anomaly_status = f"{diff_str}°C Cooler than Ingested Historical Baseline"
            status_color = "var(--indigo)"
        else:
            anomaly_status = "Aligned with Ingested Historical Baseline (±0.5°C)"
            status_color = "var(--emerald)"

        return JsonResponse({
            "status": "success",
            "filename": uploaded_file.name,
            "rows_count": len(records),
            "columns": list(records[0].keys()),
            "detected_city": primary_city,
            "cities": cities,
            "mean_temp": mean_t,
            "max_temp": max_t,
            "min_temp": min_t,
            "total_rain": total_rain,
            "current_temp": current_temp,
            "temp_anomaly": temp_diff,
            "anomaly_status": anomaly_status,
            "status_color": status_color,
            "live_curve": live_curve,
            "hist_curve": hist_curve,
            "records": records[:50],
        })
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)


