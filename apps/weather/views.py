"""Views and ViewSets for the Weather app."""
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.weather.models import WeatherObservation, WeatherReading, WeatherStation
from apps.weather.serializers import (
    WeatherObservationSerializer,
    WeatherReadingSerializer,
    WeatherStationGeoSerializer,
    WeatherStationSerializer,
)


class WeatherStationViewSet(viewsets.ModelViewSet):
    """CRUD API for WeatherStations with GeoJSON and analytics actions."""

    queryset = WeatherStation.objects.all().prefetch_related("observations")
    serializer_class = WeatherStationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "code", "created_at"]
    ordering = ["code"]

    @action(detail=False, methods=["get"], url_path="geojson")
    def geojson(self, request):
        """Return all active stations as a GeoJSON FeatureCollection."""
        stations = self.get_queryset().filter(is_active=True)
        serializer = WeatherStationGeoSerializer(stations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """Return historical observations for this station (default last 24h, or ?hours=48)."""
        station = self.get_object()
        hours = int(request.query_params.get("hours", 24))
        since = timezone.now() - timezone.timedelta(hours=hours)

        observations = station.observations.filter(timestamp__gte=since).order_by("timestamp")
        serializer = WeatherObservationSerializer(observations, many=True)
        return Response(
            {
                "station_id": station.id,
                "station_code": station.code,
                "station_name": station.name,
                "count": observations.count(),
                "readings": serializer.data,
            }
        )

    @action(detail=True, methods=["get"], url_path="predict")
    def predict(self, request, pk=None):
        """Generate ML-based weather predictions for the next 24 hours."""
        station = self.get_object()
        from apps.weather.ml import WeatherMLPredictor

        predictor = WeatherMLPredictor(station)
        prediction_data = predictor.predict_next_24h()
        return Response(prediction_data)

    @action(detail=False, methods=["get"], url_path="predictions")
    def predictions(self, request):
        """Generate ML predictions for all active stations."""
        from apps.weather.ml import WeatherMLPredictor

        stations = self.get_queryset().filter(is_active=True)
        results = []
        for station in stations:
            predictor = WeatherMLPredictor(station)
            results.append(predictor.predict_next_24h())
        return Response(results)



class WeatherObservationViewSet(viewsets.ModelViewSet):
    """CRUD API for WeatherObservations / WeatherReadings."""

    queryset = WeatherObservation.objects.select_related("station").all()
    serializer_class = WeatherObservationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        "station": ["exact"],
        "station__code": ["exact", "iexact"],
        "timestamp": ["gte", "lte", "exact"],
    }
    ordering_fields = ["timestamp", "temperature_c", "wind_speed_ms", "precipitation_mm"]
    ordering = ["-timestamp"]


class WeatherReadingViewSet(WeatherObservationViewSet):
    """Endpoint for WeatherReadings (proxy of WeatherObservation)."""

    queryset = WeatherReading.objects.select_related("station").all()
    serializer_class = WeatherReadingSerializer


import json
import urllib.request
import urllib.parse
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


@api_view(["GET"])
@permission_classes([AllowAny])
def weather_forecast_view(request):
    """Fetch current weather and 5-day daily forecast from Open-Meteo API.
    Accepts 'lat' and 'lon' query parameters with 400/502/500 error handling.
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

        open_meteo_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat_val,
            "longitude": lon_val,
            "current": "temperature_2m,weather_code,wind_speed_10m,precipitation",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "forecast_days": 5,
            "timezone": "auto",
        }

        query_str = urllib.parse.urlencode(params)
        full_url = f"{open_meteo_url}?{query_str}"

        # 3. Open-Meteo request failure -> HTTP 502
        try:
            if HAS_REQUESTS:
                resp = requests.get(full_url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
            else:
                req = urllib.request.Request(full_url, headers={"User-Agent": "WeatherApp"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            return JsonResponse(
                {"error": f"Failed to fetch weather data from Open-Meteo upstream service: {str(exc)}"},
                status=502,
            )

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

        return JsonResponse({
            "latitude": data.get("latitude", lat_val),
            "longitude": data.get("longitude", lon_val),
            "current_temperature": current.get("temperature_2m"),
            "current_weather_code": current.get("weather_code"),
            "wind_speed": current.get("wind_speed_10m"),
            "precipitation": current.get("precipitation"),
            "5_day_daily_forecast": daily_forecast,
            "daily_forecast": daily_forecast,
        })
    except Exception as exc:
        # 4. Unexpected server error -> HTTP 500
        return JsonResponse(
            {"error": f"An unexpected server error occurred: {str(exc)}"},
            status=500,
        )



