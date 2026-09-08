"""Admin configuration for the dashboard app.

No models are registered here — the dashboard app uses read-only aggregations
over data owned by other apps.
"""
from django.contrib import admin  # noqa: F401
