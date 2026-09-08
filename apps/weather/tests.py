"""Tests for Weather models, ML predictions, and APIs."""
from datetime import datetime, timedelta, timezone
from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.weather.ml import WeatherMLPredictor
from apps.weather.models import WeatherObservation, WeatherReading, WeatherStation


class WeatherModelTests(TestCase):
    def setUp(self):
        self.station = WeatherStation.objects.create(
            code="TEST01",
            name="Test Metro Station",
            location=Point(-74.006, 40.7128, srid=4326),
            elevation_m=10.0,
            is_active=True,
        )

    def test_station_creation_and_coordinates(self):
        self.assertEqual(str(self.station), "TEST01 — Test Metro Station")
        self.assertAlmostEqual(self.station.longitude, -74.006, places=3)
        self.assertAlmostEqual(self.station.latitude, 40.7128, places=3)

    def test_weather_observation_and_reading_proxy(self):
        now = datetime.now(tz=timezone.utc)
        obs = WeatherObservation.objects.create(
            station=self.station,
            timestamp=now,
            temperature_c=22.5,
            humidity_pct=55.0,
            pressure_hpa=1014.0,
            wind_speed_ms=4.2,
        )
        self.assertEqual(WeatherReading.objects.count(), 1)
        reading = WeatherReading.objects.first()
        self.assertEqual(reading.temperature_c, 22.5)
        self.assertEqual(reading.station.code, "TEST01")

    def test_ml_predictor_generation(self):
        now = datetime.now(tz=timezone.utc)
        # Create a few synthetic observations
        for i in range(15):
            WeatherObservation.objects.create(
                station=self.station,
                timestamp=now - timedelta(hours=i),
                temperature_c=20.0 + (i % 5),
                humidity_pct=60.0,
                pressure_hpa=1012.0,
                wind_speed_ms=3.0,
            )

        predictor = WeatherMLPredictor(self.station)
        result = predictor.predict_next_24h()

        self.assertEqual(result["station_code"], "TEST01")
        self.assertEqual(len(result["forecast"]), 24)
        self.assertIn("heatwave", result["hazard_risks"])
        self.assertIn("storm_squall", result["hazard_risks"])
        self.assertGreater(result["summary_24h"]["max_temp_c"], -100)


class WeatherAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.station = WeatherStation.objects.create(
            code="JFK",
            name="New York JFK",
            location=Point(-73.7781, 40.6413, srid=4326),
            is_active=True,
        )

    def test_stations_list_endpoint(self):
        response = self.client.get("/api/v1/weather/stations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get("results", data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["code"], "JFK")

    def test_stations_geojson_endpoint(self):
        response = self.client.get("/api/v1/weather/stations/geojson/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data.get("type"), "FeatureCollection")
        self.assertEqual(len(data.get("features", [])), 1)

    def test_station_predict_endpoint(self):
        response = self.client.get(f"/api/v1/weather/stations/{self.station.id}/predict/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["station_code"], "JFK")
        self.assertEqual(len(data["forecast"]), 24)
