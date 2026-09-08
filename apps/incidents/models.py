"""Models for weather-related incident tracking."""
from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Incident(models.Model):
    """A weather-related incident affecting a geographic area."""

    class Severity(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        CRITICAL = "critical", _("Critical")

    class Status(models.TextChoices):
        OPEN = "open", _("Open")
        MONITORING = "monitoring", _("Monitoring")
        RESOLVED = "resolved", _("Resolved")
        CLOSED = "closed", _("Closed")

    class IncidentType(models.TextChoices):
        FLOOD = "flood", _("Flood")
        STORM = "storm", _("Storm")
        HEATWAVE = "heatwave", _("Heatwave")
        DROUGHT = "drought", _("Drought")
        TORNADO = "tornado", _("Tornado")
        BLIZZARD = "blizzard", _("Blizzard")
        OTHER = "other", _("Other")

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    incident_type = models.CharField(
        max_length=20,
        choices=IncidentType.choices,
        default=IncidentType.OTHER,
    )
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
        default=Severity.MEDIUM,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    # Spatial field: polygon representing the affected geographic area
    affected_area = models.PolygonField(
        srid=4326,
        null=True,
        blank=True,
        help_text=_("WGS84 polygon of the affected region."),
    )
    image = models.ImageField(
        upload_to="incidents/%Y/%m/",
        null=True,
        blank=True,
        help_text=_("Photo or attachment of the incident."),
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    reported_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reported_incidents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_time"]
        verbose_name = "Incident"
        verbose_name_plural = "Incidents"
        indexes = [
            models.Index(fields=["status", "severity"]),
            models.Index(fields=["incident_type"]),
            models.Index(fields=["start_time"]),
        ]

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.title}"

    @property
    def is_active(self) -> bool:
        """Return True if the incident is currently open or being monitored."""
        return self.status in (self.Status.OPEN, self.Status.MONITORING)

    @property
    def centroid(self) -> dict | None:
        """Returns centroid longitude and latitude dict if affected_area exists."""
        if self.affected_area:
            c = self.affected_area.centroid
            return {"latitude": c.y, "longitude": c.x}
        return None


class IncidentReport(Incident):
    """Alias / Proxy model for Incident as IncidentReport."""

    class Meta:
        proxy = True
        verbose_name = "Incident Report"
        verbose_name_plural = "Incident Reports"

