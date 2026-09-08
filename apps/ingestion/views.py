"""Views for the Ingestion app."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from apps.ingestion.models import IngestionJob
from apps.ingestion.serializers import IngestionJobSerializer


class IngestionJobViewSet(viewsets.ModelViewSet):
    """API for viewing and triggering Ingestion Jobs."""

    queryset = IngestionJob.objects.all()
    serializer_class = IngestionJobSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    ordering = ["-created_at"]

    @action(detail=False, methods=["post"], url_path="trigger")
    def trigger(self, request):
        """Trigger an asynchronous or synchronous weather ingestion run."""
        from apps.ingestion.tasks import fetch_weather_data

        source = request.data.get("source", "open_meteo")
        # Dispatch Celery task or run directly
        try:
            task = fetch_weather_data.delay(source=source)
            return Response(
                {"detail": "Ingestion job queued", "task_id": task.id, "source": source},
                status=status.HTTP_202_ACCEPTED,
            )
        except Exception:
            # Fallback for standalone/local environment without running celery
            result = fetch_weather_data(source=source)
            return Response(result, status=status.HTTP_200_OK)
