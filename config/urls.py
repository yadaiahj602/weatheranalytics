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

from apps.dashboard.views import home_view

urlpatterns = [
    # Homepage - Professional Weather Analytics Dashboard
    path("", home_view, name="home"),

    # Django admin
    path("admin/", admin.site.urls),

    # OpenAPI schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),

    # App API routes
    path("api/v1/weather/", include("apps.weather.urls")),
    path("api/v1/incidents/", include("apps.incidents.urls")),
    path("api/v1/alerts/", include("apps.alerts.urls")),
    path("api/v1/ingestion/", include("apps.ingestion.urls")),
    path("api/v1/dashboard/", include("apps.dashboard.urls")),

    # Backward compatibility / shorthand routes
    path("api/weather/", include("apps.weather.urls")),
    path("api/incidents/", include("apps.incidents.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
