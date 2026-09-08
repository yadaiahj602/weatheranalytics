"""DRF Serializers for the Incidents app."""
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from apps.incidents.models import Incident, IncidentReport


class IncidentSerializer(serializers.ModelSerializer):
    """Standard serializer for Incident, supporting image uploads."""

    reported_by_username = serializers.CharField(source="reported_by.username", read_only=True, default=None, allow_null=True)
    is_active = serializers.BooleanField(read_only=True)
    centroid = serializers.ReadOnlyField()

    class Meta:
        model = Incident
        fields = [
            "id",
            "title",
            "description",
            "incident_type",
            "severity",
            "status",
            "is_active",
            "affected_area",
            "centroid",
            "image",
            "start_time",
            "end_time",
            "reported_by",
            "reported_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "reported_by"]


class IncidentGeoSerializer(GeoFeatureModelSerializer):
    """GeoJSON Feature serializer for Incident affected areas."""

    reported_by_username = serializers.CharField(source="reported_by.username", read_only=True, default=None, allow_null=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Incident
        geo_field = "affected_area"
        fields = [
            "id",
            "title",
            "description",
            "incident_type",
            "severity",
            "status",
            "is_active",
            "image",
            "start_time",
            "end_time",
            "reported_by_username",
        ]


class IncidentReportSerializer(IncidentSerializer):
    """Serializer for IncidentReport proxy model."""

    class Meta(IncidentSerializer.Meta):
        model = IncidentReport
