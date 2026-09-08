"""URLs for the Alerts app."""
from rest_framework.routers import DefaultRouter

from apps.alerts.views import AlertEventViewSet, AlertRuleViewSet

router = DefaultRouter()
router.register(r"rules", AlertRuleViewSet, basename="alert-rule")
router.register(r"events", AlertEventViewSet, basename="alert-event")

urlpatterns = router.urls
