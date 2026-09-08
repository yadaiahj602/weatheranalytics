"""URLs for the Ingestion app."""
from rest_framework.routers import DefaultRouter

from apps.ingestion.views import IngestionJobViewSet

router = DefaultRouter()
router.register(r"jobs", IngestionJobViewSet, basename="ingestion-job")

urlpatterns = router.urls
