"""Core weather domain models with GeoDjango spatial fields."""
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class WeatherStation(models.Model):
    """A physical weather observation station with a known geographic location."""

    code = models.CharField(
        max_length=20,
        unique=True,
        help_text=_("Station identifier code (e.g. IATA or WMO code)."),
    )
    name = models.CharField(max_length=200)
    location = models.PointField(
        srid=4326,
        help_text=_("WGS84 point geometry (longitude, latitude)."),
    )
    elevation_m = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Elevation above sea level in metres."),
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Weather Station"
        verbose_name_plural = "Weather Stations"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"

    @property
    def latitude(self) -> float | None:
        return self.location.y if self.location else None

    @property
    def longitude(self) -> float | None:
        return self.location.x if self.location else None


class WeatherObservation(models.Model):
    """A single weather observation recorded at a station."""

    station = models.ForeignKey(
        WeatherStation,
        on_delete=models.CASCADE,
        related_name="observations",
    )
    timestamp = models.DateTimeField(
        db_index=True,
        help_text=_("UTC timestamp of the observation."),
    )

    # Meteorological measurements (all nullable to support partial observations)
    temperature_c = models.FloatField(null=True, blank=True, help_text=_("Air temperature (°C)."))
    humidity_pct = models.FloatField(null=True, blank=True, help_text=_("Relative humidity (%%)."))
    pressure_hpa = models.FloatField(null=True, blank=True, help_text=_("Sea-level pressure (hPa)."))
    wind_speed_ms = models.FloatField(null=True, blank=True, help_text=_("Wind speed (m/s)."))
    wind_direction_deg = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Wind direction in degrees from true north (0–360)."),
    )
    precipitation_mm = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Precipitation accumulation (mm)."),
    )
    cloud_cover_pct = models.FloatField(null=True, blank=True, help_text=_("Cloud cover (%%)."))
    visibility_m = models.FloatField(null=True, blank=True, help_text=_("Visibility (metres)."))

    raw_data = models.JSONField(
        null=True,
        blank=True,
        help_text=_("Original JSON payload from the source API for auditing."),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Weather Observation"
        verbose_name_plural = "Weather Observations"
        unique_together = [("station", "timestamp")]
        indexes = [
            models.Index(fields=["station", "timestamp"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.station.code} @ {self.timestamp:%Y-%m-%d %H:%M UTC}"


class WeatherReading(WeatherObservation):
    """Alias / Proxy model for WeatherObservation as WeatherReading."""

    class Meta:
        proxy = True
        verbose_name = "Weather Reading"
        verbose_name_plural = "Weather Readings"

