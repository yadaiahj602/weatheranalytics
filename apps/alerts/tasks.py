"""Celery tasks for the alerts app."""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def evaluate_alert_rules(self) -> dict:
    """Evaluate all active alert rules against recent observations.

    For each rule, checks observations from the last 15 minutes. If the
    threshold condition is breached, creates an AlertEvent and queues
    a dispatch_notification task.

    Returns:
        A dict with counts of rules checked and events created.
    """
    from apps.alerts.models import AlertEvent, AlertRule
    from apps.weather.models import WeatherObservation

    since = timezone.now() - timedelta(minutes=15)
    rules = AlertRule.objects.filter(is_active=True).select_related("station")
    events_created = 0

    for rule in rules:
        observations = WeatherObservation.objects.filter(timestamp__gte=since)
        if rule.station:
            observations = observations.filter(station=rule.station)

        for obs in observations:
            if _threshold_breached(rule, obs):
                event = AlertEvent.objects.create(rule=rule, observation=obs)
                try:
                    dispatch_notification.delay(event.pk)
                except Exception:
                    dispatch_notification(event.pk)
                events_created += 1


    logger.info(
        "Alert evaluation complete: rules_checked=%s events_created=%s",
        rules.count(),
        events_created,
    )
    return {"rules_checked": rules.count(), "events_created": events_created}


def _threshold_breached(rule, observation) -> bool:
    """Return True if the observation value breaches the rule threshold."""
    from apps.alerts.models import AlertRule

    mapping = {
        AlertRule.ConditionType.TEMPERATURE_ABOVE: ("temperature_c", lambda v, t: v > t),
        AlertRule.ConditionType.TEMPERATURE_BELOW: ("temperature_c", lambda v, t: v < t),
        AlertRule.ConditionType.WIND_SPEED_ABOVE: ("wind_speed_ms", lambda v, t: v > t),
        AlertRule.ConditionType.PRECIPITATION_ABOVE: ("precipitation_mm", lambda v, t: v > t),
        AlertRule.ConditionType.HUMIDITY_ABOVE: ("humidity_pct", lambda v, t: v > t),
        AlertRule.ConditionType.HUMIDITY_BELOW: ("humidity_pct", lambda v, t: v < t),
        AlertRule.ConditionType.PRESSURE_BELOW: ("pressure_hpa", lambda v, t: v < t),
    }
    if rule.condition_type not in mapping:
        return False

    field_name, comparator = mapping[rule.condition_type]
    value = getattr(observation, field_name)
    if value is None:
        return False
    return comparator(value, rule.threshold)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def dispatch_notification(self, event_id: int) -> None:
    """Send a notification for a triggered AlertEvent.

    Args:
        event_id: Primary key of the AlertEvent to notify about.
    """
    from datetime import datetime
    from apps.alerts.models import AlertEvent

    try:
        event = AlertEvent.objects.select_related("rule", "observation__station").get(pk=event_id)
    except AlertEvent.DoesNotExist:
        logger.warning("AlertEvent %s not found; skipping dispatch.", event_id)
        return

    try:
        # --- Replace with real channel-specific dispatch logic ---
        channel = event.rule.channel
        recipients = event.rule.recipients
        logger.info(
            "Dispatching alert: event_id=%s channel=%s recipients=%s",
            event_id,
            channel,
            recipients,
        )
        # ----------------------------------------------------------

        event.notify_status = AlertEvent.NotifyStatus.SENT
        event.notify_sent_at = datetime.now(tz=timezone.utc)
        event.save(update_fields=["notify_status", "notify_sent_at"])

    except Exception as exc:
        event.notify_status = AlertEvent.NotifyStatus.FAILED
        event.error_message = str(exc)
        event.save(update_fields=["notify_status", "error_message"])
        raise self.retry(exc=exc)
