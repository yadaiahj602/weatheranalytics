"""Views and ViewSets for the Incidents app."""
from rest_framework import parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.incidents.models import Incident, IncidentReport
from apps.incidents.serializers import (
    IncidentGeoSerializer,
    IncidentReportSerializer,
    IncidentSerializer,
)


class IncidentViewSet(viewsets.ModelViewSet):
    """CRUD API for Incidents with GeoJSON layer support and image uploads."""

    queryset = Incident.objects.select_related("reported_by").all()
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "severity", "incident_type"]
    search_fields = ["title", "description"]
    ordering_fields = ["start_time", "severity", "created_at"]
    ordering = ["-start_time"]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(reported_by=user)

    @action(detail=False, methods=["get"], url_path="geojson")
    def geojson(self, request):
        """Return all incidents that have an affected_area as a GeoJSON FeatureCollection."""
        incidents = self.get_queryset().filter(affected_area__isnull=False)
        status_param = request.query_params.get("status")
        if status_param:
            incidents = incidents.filter(status=status_param)
        serializer = IncidentGeoSerializer(incidents, many=True)
        return Response(serializer.data)


class IncidentReportViewSet(IncidentViewSet):
    """Endpoint for IncidentReport proxy model."""

    queryset = IncidentReport.objects.select_related("reported_by").all()
    serializer_class = IncidentReportSerializer
