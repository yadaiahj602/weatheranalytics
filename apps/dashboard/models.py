"""Dashboard app models.

The dashboard app does not own primary data; it provides aggregated views
over data owned by other apps. No persistent models are defined here.
"""
# No models — aggregations are performed via query-layer views and annotations
# on models from apps.weather, apps.incidents, and apps.alerts.
