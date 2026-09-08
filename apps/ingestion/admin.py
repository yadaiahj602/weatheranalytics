"""Admin configuration for the ingestion app."""
from django.contrib import admin

from .models import IngestionJob


@admin.register(IngestionJob)
class IngestionJobAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "status", "records_processed", "started_at", "finished_at", "created_at")
    list_filter = ("source", "status")
    search_fields = ("source", "error_message")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
