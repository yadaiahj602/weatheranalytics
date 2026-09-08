"""URL configuration for weatherplatform project."""
from django.contrib import admin
from django.urls import path
from core.views import (
    weather_forecast_view,
    demo_cities_weather_view,
    dashboard_page,
    weather_page,
    cities_page,
    forecast_page,
    prediction_page,
    alerts_page,
    incidents_page,
    assistant_page,
    alerts_view,
    ai_chat_view,
    create_incident_view,
    list_incidents_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # ── User-Facing Web Pages (HTML) ──────────────────────────
    path("", dashboard_page, name="dashboard"),
    path("dashboard/", dashboard_page, name="dashboard-alias"),
    path("weather/", weather_page, name="weather"),
    path("cities/", cities_page, name="cities"),
    path("forecast/", forecast_page, name="forecast"),
    path("prediction/", prediction_page, name="prediction"),
    path("predictions/", prediction_page, name="predictions"),
    path("alerts/", alerts_page, name="alerts"),
    path("incidents/", incidents_page, name="incidents"),
    path("citizen-reports/", incidents_page, name="citizen-reports"),
    path("assistant/", assistant_page, name="assistant"),
    path("ai/", assistant_page, name="ai-alias"),

    # ── Silent Backend APIs (Used internally via AJAX/Fetch) ──
    path("api/weather/", weather_forecast_view, name="api-weather-forecast"),
    path("api/weather/forecast/", weather_forecast_view, name="api-weather-forecast-nested"),
    path("api/weather/cities/", demo_cities_weather_view, name="api-weather-cities"),
    path("api/alerts/", alerts_view, name="api-alerts"),
    path("api/v1/alerts/", alerts_view, name="api-v1-alerts"),
    path("api/incidents/report/", create_incident_view, name="api-incident-report"),
    path("api/incidents/list/", list_incidents_view, name="api-incident-list"),
    path("api/ai/chat/", ai_chat_view, name="api-ai-chat"),
    path("api/v1/ai/chat/", ai_chat_view, name="api-v1-ai-chat"),
]