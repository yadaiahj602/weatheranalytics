"""Celery application instance for weatherplatform."""
import os

from celery import Celery
from celery.schedules import crontab

# Default Django settings module for the Celery process.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("weatherplatform")

# Namespace all Celery config keys with CELERY_ in Django settings.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed apps.
app.autodiscover_tasks()

# ---------------------------------------------------------------------------
# Beat schedule (placeholder periodic tasks)
# ---------------------------------------------------------------------------
app.conf.beat_schedule = {
    # Fetch weather data every 15 minutes
    "fetch-weather-data-every-15min": {
        "task": "apps.ingestion.tasks.fetch_weather_data",
        "schedule": crontab(minute="*/15"),
        "args": (),
    },
    # Evaluate alert rules every 5 minutes
    "evaluate-alert-rules-every-5min": {
        "task": "apps.alerts.tasks.evaluate_alert_rules",
        "schedule": crontab(minute="*/5"),
        "args": (),
    },
}

app.conf.timezone = "UTC"


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Diagnostic task that prints the request info."""
    print(f"Request: {self.request!r}")
