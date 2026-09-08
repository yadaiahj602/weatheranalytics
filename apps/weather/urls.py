"""URLs for the Weather app."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.weather.views import (
    WeatherObservationViewSet,
    WeatherReadingViewSet,
    WeatherStationViewSet,
    weather_forecast_view,
)
from core.views import demo_cities_weather_view

router = DefaultRouter()
router.register(r"stations", WeatherStationViewSet, basename="weather-station")
router.register(r"observations", WeatherObservationViewSet, basename="weather-observation")
router.register(r"readings", WeatherReadingViewSet, basename="weather-reading")

urlpatterns = [
    path("cities/", demo_cities_weather_view, name="weather-cities-api"),
    path("forecast/", weather_forecast_view, name="weather-forecast-api"),
    path("", weather_forecast_view, name="weather-forecast-root"),
] + router.urls
