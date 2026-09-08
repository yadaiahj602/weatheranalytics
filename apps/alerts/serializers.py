"""Serializers for the Alerts app."""
from rest_framework import serializers

from apps.alerts.models import AlertEvent, AlertRule


class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer for AlertRule."""

    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = AlertRule
        fields = [
            "id",
            "name",
            "description",
            "condition_type",
            "threshold",
            "station",
            "station_name",
            "channel",
            "recipients",
            "is_active",
            "created_at",
            "updated_at",
        ]


class AlertEventSerializer(serializers.ModelSerializer):
    """Serializer for AlertEvent."""

    rule_name = serializers.CharField(source="rule.name", read_only=True)
    condition_type = serializers.CharField(source="rule.condition_type", read_only=True)
    threshold = serializers.FloatField(source="rule.threshold", read_only=True)
    station_name = serializers.CharField(source="observation.station.name", read_only=True)

    class Meta:
        model = AlertEvent
        fields = [
            "id",
            "rule",
            "rule_name",
            "condition_type",
            "threshold",
            "observation",
            "station_name",
            "triggered_at",
            "notify_status",
            "notify_sent_at",
            "error_message",
        ]
