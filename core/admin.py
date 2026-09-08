from django.contrib import admin
from .models import WeatherReading, IncidentReport


@admin.register(WeatherReading)
class WeatherReadingAdmin(admin.ModelAdmin):
    list_display = ("location_name", "temperature", "rainfall", "wind", "lat", "lon", "timestamp")
    list_filter = ("location_name", "timestamp")
    search_fields = ("location_name",)


@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ("category", "description", "lat", "lon", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("category", "description")
