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


class IncidentDataAPI(APIView):
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
