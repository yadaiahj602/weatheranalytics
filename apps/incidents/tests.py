"""Tests for Incidents models and APIs."""
from datetime import datetime, timezone
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.incidents.models import Incident, IncidentReport


class IncidentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="operator", password="password")
        self.now = datetime.now(tz=timezone.utc)
        self.poly = Polygon([
            (-74.1, 40.5),
            (-73.8, 40.5),
            (-73.8, 40.8),
            (-74.1, 40.8),
            (-74.1, 40.5),
        ], srid=4326)

        self.incident = Incident.objects.create(
            title="Severe Flash Flood",
            description="High water levels observed in coastal sector.",
            incident_type=Incident.IncidentType.FLOOD,
            severity=Incident.Severity.CRITICAL,
            status=Incident.Status.OPEN,
            affected_area=self.poly,
            start_time=self.now,
        )

    def test_incident_and_report_proxy(self):
        self.assertTrue(self.incident.is_active)
        self.assertIsNotNone(self.incident.centroid)
        self.assertEqual(IncidentReport.objects.count(), 1)
        report = IncidentReport.objects.first()
        self.assertEqual(report.title, "Severe Flash Flood")

    def test_incidents_list_endpoint(self):
        response = self.client.get("/api/v1/incidents/incidents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get("results", data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["severity"], "critical")

    def test_incidents_geojson_endpoint(self):
        response = self.client.get("/api/v1/incidents/incidents/geojson/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data.get("type"), "FeatureCollection")
        self.assertEqual(len(data.get("features", [])), 1)

    def test_incident_status_patch(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/api/v1/incidents/incidents/{self.incident.id}/",
            {"status": "resolved"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, "resolved")
        self.assertFalse(self.incident.is_active)
