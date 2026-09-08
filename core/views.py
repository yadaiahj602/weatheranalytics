import json
import logging
import urllib.request
import urllib.parse
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

DEMO_CITIES = [
    {"name": "Bengaluru", "latitude": 12.9716, "longitude": 77.5946},
    {"name": "Mumbai", "latitude": 19.0760, "longitude": 72.8777},
    {"name": "Delhi", "latitude": 28.6139, "longitude": 77.2090},
    {"name": "Chennai", "latitude": 13.0827, "longitude": 80.2707},
]


def fetch_open_meteo_forecast(lat_val, lon_val):
    """Fetch current weather and 5-day daily forecast from Open-Meteo."""
    open_meteo_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat_val,
        "longitude": lon_val,
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "forecast_days": 5,
        "timezone": "auto",
    }

    query_str = urllib.parse.urlencode(params)
    full_url = f"{open_meteo_url}?{query_str}"

    if HAS_REQUESTS:
        resp = requests.get(full_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    else:
        req = urllib.request.Request(full_url, headers={"User-Agent": "WeatherApp"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

    current = data.get("current", {})
    daily = data.get("daily", {})

    daily_forecast = []
    dates = daily.get("time", [])
    weather_codes = daily.get("weather_code", [])
    temp_max = daily.get("temperature_2m_max", [])
    temp_min = daily.get("temperature_2m_min", [])

    for i in range(len(dates)):
        daily_forecast.append({
            "date": dates[i],
            "weather_code": weather_codes[i] if i < len(weather_codes) else None,
            "temperature_max": temp_max[i] if i < len(temp_max) else None,
            "temperature_min": temp_min[i] if i < len(temp_min) else None,
        })

    return {
        "latitude": data.get("latitude", lat_val),
        "longitude": data.get("longitude", lon_val),
        "current_temperature": current.get("temperature_2m"),
        "current_weather_code": current.get("weather_code"),
        "wind_speed": current.get("wind_speed_10m"),
        "5_day_daily_forecast": daily_forecast,
        "daily_forecast": daily_forecast,
    }


@require_GET
def weather_forecast_view(request):
    """Fetch current weather and 5-day daily forecast from Open-Meteo API.
    Accepts 'lat' and 'lon' query parameters with comprehensive error handling.
    """
    try:
        lat = request.GET.get("lat") or request.GET.get("latitude")
        lon = request.GET.get("lon") or request.GET.get("longitude") or request.GET.get("lng")

        # 1. Missing lat/lon -> HTTP 400
        if not lat or not lon:
            return JsonResponse(
                {"error": "Both 'lat' and 'lon' query parameters are required."},
                status=400,
            )

        # 2. Invalid coordinates -> HTTP 400
        try:
            lat_val = float(lat)
            lon_val = float(lon)
            if not (-90.0 <= lat_val <= 90.0) or not (-180.0 <= lon_val <= 180.0):
                return JsonResponse(
                    {"error": "Invalid coordinates range. Latitude must be between -90 and 90, Longitude between -180 and 180."},
                    status=400,
                )
        except (ValueError, TypeError):
            return JsonResponse(
                {"error": "'lat' and 'lon' query parameters must be valid numeric floats."},
                status=400,
            )

        # 3. Open-Meteo request failure -> HTTP 502
        try:
            weather_data = fetch_open_meteo_forecast(lat_val, lon_val)
            return JsonResponse(weather_data)
        except Exception as exc:
            logger.error("Open-Meteo API request failed: %s", exc)
            return JsonResponse(
                {"error": f"Failed to fetch weather data from Open-Meteo upstream service: {str(exc)}"},
                status=502,
            )

    except Exception as exc:
        # 4. Unexpected server error -> HTTP 500
        logger.exception("Unexpected server error in weather_forecast_view: %s", exc)
        return JsonResponse(
            {"error": f"An unexpected server error occurred: {str(exc)}"},
            status=500,
        )


@require_GET
def demo_cities_weather_view(request):
    """Return weather data for 4 hardcoded demo cities:
    Bengaluru, Mumbai, Delhi, Chennai.
    """
    try:
        results = []
        for city in DEMO_CITIES:
            try:
                weather = fetch_open_meteo_forecast(city["latitude"], city["longitude"])
                results.append({
                    "city": city["name"],
                    "name": city["name"],
                    **weather,
                })
            except Exception as exc:
                results.append({
                    "city": city["name"],
                    "name": city["name"],
                    "latitude": city["latitude"],
                    "longitude": city["longitude"],
                    "error": f"Failed to fetch weather data: {str(exc)}",
                })

        return JsonResponse({
            "count": len(results),
            "cities": results,
        })
    except Exception as exc:
        logger.exception("Unexpected server error in demo_cities_weather_view: %s", exc)
        return JsonResponse(
            {"error": f"An unexpected server error occurred: {str(exc)}"},
            status=500,
        )
