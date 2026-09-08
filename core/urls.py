from django.urls import path
from .views import weather_forecast_view, demo_cities_weather_view

urlpatterns = [
    path("weather/", weather_forecast_view, name="weather-forecast"),
    path("weather/forecast/", weather_forecast_view, name="weather-forecast-detail"),
    path("weather/cities/", demo_cities_weather_view, name="weather-cities"),
    path("weather/cities", demo_cities_weather_view, name="weather-cities-no-slash"),
]
