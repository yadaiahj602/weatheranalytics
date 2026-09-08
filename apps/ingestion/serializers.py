"""Serializers for the Ingestion app."""
from rest_framework import serializers

from apps.ingestion.models import IngestionJob


class IngestionJobSerializer(serializers.ModelSerializer):
    """Serializer for IngestionJob."""

    class Meta:
        model = IngestionJob
        fields = [
            "id",
            "source",
            "status",
            "started_at",
            "finished_at",
            "records_processed",
            "error_message",
            "created_at",
            "updated_at",
        ]
