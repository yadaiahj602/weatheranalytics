"""URLs for the Incidents app."""
from rest_framework.routers import DefaultRouter

from apps.incidents.views import IncidentReportViewSet, IncidentViewSet

router = DefaultRouter()
router.register(r"incidents", IncidentViewSet, basename="incident")
router.register(r"reports", IncidentReportViewSet, basename="incident-report")

urlpatterns = router.urls
