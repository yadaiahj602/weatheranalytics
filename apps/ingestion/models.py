"""Models for the ingestion app."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class IngestionJob(models.Model):
    """Tracks a single data ingestion job from an external source."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        RUNNING = "running", _("Running")
        SUCCESS = "success", _("Success")
        FAILED = "failed", _("Failed")

    class Source(models.TextChoices):
        OPEN_METEO = "open_meteo", _("Open-Meteo")
        OPENWEATHERMAP = "owm", _("OpenWeatherMap")
        FILE_UPLOAD = "file_upload", _("File Upload")
        MANUAL = "manual", _("Manual")

    source = models.CharField(
        max_length=50,
        choices=Source.choices,
        default=Source.MANUAL,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    records_processed = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Ingestion Job"
        verbose_name_plural = "Ingestion Jobs"

    def __str__(self) -> str:
        return f"[{self.source}] {self.status} @ {self.created_at:%Y-%m-%d %H:%M}"
