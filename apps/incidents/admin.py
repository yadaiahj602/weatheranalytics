"""Admin configuration for the incidents app."""
from django.contrib.gis import admin

from .models import Incident


@admin.register(Incident)
class IncidentAdmin(admin.GISModelAdmin):
    list_display = (
        "title",
        "incident_type",
        "severity",
        "status",
        "start_time",
        "end_time",
        "reported_by",
    )
    list_filter = ("incident_type", "severity", "status")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "start_time"
