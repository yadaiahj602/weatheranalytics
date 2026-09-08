"""Views for the Alerts app."""
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from apps.alerts.models import AlertEvent, AlertRule
from apps.alerts.serializers import AlertEventSerializer, AlertRuleSerializer


class AlertRuleViewSet(viewsets.ModelViewSet):
    """CRUD API for managing Alert Rules."""

    queryset = AlertRule.objects.select_related("station").all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_active", "condition_type", "channel", "station"]
    search_fields = ["name", "description"]
    ordering = ["name"]


class AlertEventViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API for triggered Alert Events."""

    queryset = AlertEvent.objects.select_related("rule", "observation", "observation__station").all()
    serializer_class = AlertEventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["rule", "notify_status"]
    ordering = ["-triggered_at"]
