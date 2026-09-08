from django.db import models


class WeatherReading(models.Model):
    """Weather observation readings for a specific location."""
    location_name = models.CharField(max_length=200)
    lat = models.FloatField()
    lon = models.FloatField()
    timestamp = models.DateTimeField()
    temperature = models.FloatField(help_text="Temperature in Celsius")
    rainfall = models.FloatField(default=0.0, help_text="Rainfall in mm")
    wind = models.FloatField(default=0.0, help_text="Wind speed")

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Weather Reading"
        verbose_name_plural = "Weather Readings"

    def __str__(self):
        return f"{self.location_name} - {self.temperature}°C @ {self.timestamp}"


from django.contrib.auth.models import User


class IncidentReport(models.Model):
    """Incident report filed for severe weather or emergency events."""
    description = models.TextField()
    category = models.CharField(max_length=100)
    lat = models.FloatField()
    lon = models.FloatField()
    author = models.CharField(max_length=150, default="Citizen Reporter", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Incident Report"
        verbose_name_plural = "Incident Reports"

    def __str__(self):
        return f"[{self.category}] {self.description[:40]}"


class UserPreference(models.Model):
    """Store user personal weather preferences, favorite cities, and saved alerts."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="preference")
    home_city = models.CharField(max_length=100, default="Bengaluru")
    favorite_cities = models.JSONField(default=list)
    alert_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"

