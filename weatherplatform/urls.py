"""URL configuration for weatherplatform project."""
from django.contrib import admin
from django.urls import path
from core.views import weather_forecast_view, demo_cities_weather_view

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Single city forecast endpoints (lat, lon)
    path("weather/", weather_forecast_view, name="weather-forecast"),
    path("weather/forecast/", weather_forecast_view, name="weather-forecast-nested"),
    path("api/weather/", weather_forecast_view, name="api-weather-forecast"),
    path("api/weather/forecast/", weather_forecast_view, name="api-weather-forecast-nested"),

    # 4 Demo cities endpoints (/api/weather/cities/ and /weather/cities/)
    path("api/weather/cities/", demo_cities_weather_view, name="api-weather-cities"),
    path("weather/cities/", demo_cities_weather_view, name="weather-cities"),
]