"""Admin configuration for the weather app."""
from django.contrib.gis import admin

from .models import WeatherObservation, WeatherStation


@admin.register(WeatherStation)
class WeatherStationAdmin(admin.GISModelAdmin):
    list_display = ("code", "name", "elevation_m", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(WeatherObservation)
class WeatherObservationAdmin(admin.ModelAdmin):
    list_display = (
        "station",
        "timestamp",
        "temperature_c",
        "humidity_pct",
        "pressure_hpa",
        "wind_speed_ms",
        "precipitation_mm",
    )
    list_filter = ("station",)
    search_fields = ("station__code", "station__name")
    readonly_fields = ("created_at",)
    date_hierarchy = "timestamp"
