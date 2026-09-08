"""URL patterns for the dashboard app."""

from django.urls import path

from .views import (
    DashboardSummaryView,
    IncidentReportView,
    IncidentListView,
    IncidentMapView,
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardSummaryView.as_view(), name="index"),
    path("summary/", DashboardSummaryView.as_view(), name="summary"),
    path("incidents/report/", IncidentReportView.as_view(), name="incident-report"),
    path("incidents/data/", IncidentListView.as_view(), name="incident-data"),
    path("incidents/map/", IncidentMapView.as_view(), name="incident-map"),
]
