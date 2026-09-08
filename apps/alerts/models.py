"""Models for the alerts app."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.weather.models import WeatherObservation, WeatherStation


class AlertRule(models.Model):
    """A configurable rule that triggers alerts when weather thresholds are breached."""

    class ConditionType(models.TextChoices):
        TEMPERATURE_ABOVE = "temp_above", _("Temperature Above")
        TEMPERATURE_BELOW = "temp_below", _("Temperature Below")
        WIND_SPEED_ABOVE = "wind_above", _("Wind Speed Above")
        PRECIPITATION_ABOVE = "precip_above", _("Precipitation Above")
        HUMIDITY_ABOVE = "humidity_above", _("Humidity Above")
        HUMIDITY_BELOW = "humidity_below", _("Humidity Below")
        PRESSURE_BELOW = "pressure_below", _("Pressure Below")

    class NotificationChannel(models.TextChoices):
        EMAIL = "email", _("Email")
        SMS = "sms", _("SMS")
        WEBHOOK = "webhook", _("Webhook")
        SLACK = "slack", _("Slack")

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, default="")
    condition_type = models.CharField(
        max_length=20,
        choices=ConditionType.choices,
    )
    threshold = models.FloatField(
        help_text=_("Numeric threshold value that triggers this rule."),
    )
    station = models.ForeignKey(
        WeatherStation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="alert_rules",
        help_text=_("If set, rule applies only to this station. Leave blank for all stations."),
    )
    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        default=NotificationChannel.EMAIL,
    )
    recipients = models.JSONField(
        default=list,
        help_text=_("List of recipient addresses/URLs for the chosen channel."),
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Alert Rule"
        verbose_name_plural = "Alert Rules"

    def __str__(self) -> str:
        return f"{self.name} ({self.condition_type} {self.threshold})"


class AlertEvent(models.Model):
    """Recorded instance of an alert rule being triggered by an observation."""

    class NotifyStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        SENT = "sent", _("Sent")
        FAILED = "failed", _("Failed")

    rule = models.ForeignKey(
        AlertRule,
        on_delete=models.CASCADE,
        related_name="events",
    )
    observation = models.ForeignKey(
        WeatherObservation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="alert_events",
    )
    triggered_at = models.DateTimeField(auto_now_add=True)
    notify_status = models.CharField(
        max_length=20,
        choices=NotifyStatus.choices,
        default=NotifyStatus.PENDING,
    )
    notify_sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-triggered_at"]
        verbose_name = "Alert Event"
        verbose_name_plural = "Alert Events"

    def __str__(self) -> str:
        return f"{self.rule.name} @ {self.triggered_at:%Y-%m-%d %H:%M}"
