"""Root URL configuration for weatherplatform."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from django.conf import settings
from django.conf.urls.static import static
import debug_toolbar

from apps.dashboard.views import (
    home_view,
    dashboard_page,
    weather_page,
    cities_page,
    forecast_page,
    prediction_page,
    alerts_page,
    incidents_page,
    assistant_page,
    historical_page,
    login_view,
    register_view,
    logout_view,
    profile_view,
    api_historical_weather,
    api_save_favorite,
    api_dataset_upload,
)
from core.views import (
    weather_forecast_view,
    demo_cities_weather_view,
    alerts_view,
    ai_chat_view,
    create_incident_view,
    list_incidents_view,
)

urlpatterns = [
    # ── User-Facing Web Pages (HTML) ──────────────────────────────
    path("", login_view, name="root-login"),
    path("dashboard/", dashboard_page, name="dashboard"),
    path("weather/", weather_page, name="weather"),
    path("cities/", cities_page, name="cities"),
    path("forecast/", forecast_page, name="forecast"),
    path("prediction/", prediction_page, name="prediction"),
    path("predictions/", prediction_page, name="predictions"),
    path("historical/", historical_page, name="historical"),
    path("alerts/", alerts_page, name="alerts"),
    path("incidents/", incidents_page, name="incidents"),
    path("citizen-reports/", incidents_page, name="citizen-reports"),
    path("assistant/", assistant_page, name="assistant"),
    path("ai/", assistant_page, name="ai-alias"),

    # ── Authentication & User Profile ──────────────────────────────
    path("login/", login_view, name="login"),
    path("signin/", login_view, name="signin"),
    path("register/", register_view, name="register"),
    path("signup/", register_view, name="signup"),
    path("logout/", logout_view, name="logout"),
    path("signout/", logout_view, name="signout"),
    path("profile/", profile_view, name="profile"),

    # ── Silent Backend APIs ────────────────────────────────────────
    path("api/weather/historical/", api_historical_weather, name="api-historical-weather"),
    path("api/auth/favorites/", api_save_favorite, name="api-auth-favorites"),
    path("api/dataset/upload/", api_dataset_upload, name="api-dataset-upload"),

    # Legacy home (kept for backward compat)
    path("home/", home_view, name="home"),

    # ── Django Admin ───────────────────────────────────────────────
    path("admin/", admin.site.urls),

    # ── OpenAPI / Swagger Docs ─────────────────────────────────────
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # ── Weather Telemetry APIs ─────────────────────────────────────
    path("api/weather/", weather_forecast_view, name="api-weather"),
    path("api/weather/forecast/", weather_forecast_view, name="api-weather-forecast"),
    path("api/weather/cities/", demo_cities_weather_view, name="api-weather-cities"),
    path("weather/cities/", demo_cities_weather_view, name="weather-cities"),

    # ── Alerts APIs ────────────────────────────────────────────────
    path("api/alerts/", alerts_view, name="api-alerts"),
    path("api/v1/alerts-live/", alerts_view, name="api-v1-alerts-live"),

    # ── Incident Reporting APIs ────────────────────────────────────
    path("api/incidents/report/", create_incident_view, name="api-incident-report"),
    path("api/incidents/list/", list_incidents_view, name="api-incident-list"),

    # ── AI Chat API ────────────────────────────────────────────────
    path("api/ai/chat/", ai_chat_view, name="api-ai-chat"),
    path("api/v1/ai/chat/", ai_chat_view, name="api-v1-ai-chat"),

    # ── DRF App routes (versioned) ─────────────────────────────────
    path("api/v1/weather/", include("apps.weather.urls")),
    path("api/v1/incidents/", include("apps.incidents.urls")),
    path("api/v1/django-alerts/", include("apps.alerts.urls")),
    path("api/v1/ingestion/", include("apps.ingestion.urls")),
    path("api/v1/dashboard/", include("apps.dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
