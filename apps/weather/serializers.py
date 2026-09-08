"""DRF Serializers for the Weather app."""
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from apps.weather.models import WeatherObservation, WeatherReading, WeatherStation


class WeatherStationSerializer(serializers.ModelSerializer):
    """Standard serializer for WeatherStation with flattened latitude and longitude."""

    latitude = serializers.FloatField(read_only=True)
    longitude = serializers.FloatField(read_only=True)
    latest_reading = serializers.SerializerMethodField()

    class Meta:
        model = WeatherStation
        fields = [
            "id",
            "code",
            "name",
            "latitude",
            "longitude",
            "elevation_m",
            "is_active",
            "latest_reading",
            "created_at",
            "updated_at",
        ]

    def get_latest_reading(self, obj: WeatherStation):
        latest = obj.observations.order_by("-timestamp").first()
        if not latest:
            return None
        return {
            "timestamp": latest.timestamp,
            "temperature_c": latest.temperature_c,
            "humidity_pct": latest.humidity_pct,
            "pressure_hpa": latest.pressure_hpa,
            "wind_speed_ms": latest.wind_speed_ms,
            "precipitation_mm": latest.precipitation_mm,
        }


class WeatherStationGeoSerializer(GeoFeatureModelSerializer):
    """GeoJSON Feature serializer for WeatherStation for map layers."""

    latest_reading = serializers.SerializerMethodField()

    class Meta:
        model = WeatherStation
        geo_field = "location"
        fields = [
            "id",
            "code",
            "name",
            "elevation_m",
            "is_active",
            "latest_reading",
        ]

    def get_latest_reading(self, obj: WeatherStation):
        latest = obj.observations.order_by("-timestamp").first()
        if not latest:
            return None
        return {
            "timestamp": latest.timestamp,
            "temperature_c": latest.temperature_c,
            "humidity_pct": latest.humidity_pct,
            "pressure_hpa": latest.pressure_hpa,
            "wind_speed_ms": latest.wind_speed_ms,
        }


class WeatherObservationSerializer(serializers.ModelSerializer):
    """Serializer for WeatherObservation."""

    station_code = serializers.CharField(source="station.code", read_only=True)
    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = WeatherObservation
        fields = [
            "id",
            "station",
            "station_code",
            "station_name",
            "timestamp",
            "temperature_c",
            "humidity_pct",
            "pressure_hpa",
            "wind_speed_ms",
            "wind_direction_deg",
            "precipitation_mm",
            "cloud_cover_pct",
            "visibility_m",
            "raw_data",
            "created_at",
        ]


class WeatherReadingSerializer(WeatherObservationSerializer):
    """Serializer for WeatherReading proxy model."""

    class Meta(WeatherObservationSerializer.Meta):
        model = WeatherReading
