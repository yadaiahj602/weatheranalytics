"""Admin configuration for the alerts app."""
from django.contrib import admin

from .models import AlertEvent, AlertRule


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "condition_type", "threshold", "station", "channel", "is_active", "created_at")
    list_filter = ("condition_type", "channel", "is_active")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(AlertEvent)
class AlertEventAdmin(admin.ModelAdmin):
    list_display = ("rule", "observation", "triggered_at", "notify_status", "notify_sent_at")
    list_filter = ("notify_status", "rule")
    search_fields = ("rule__name",)
    readonly_fields = ("triggered_at",)
    date_hierarchy = "triggered_at"
