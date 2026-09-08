"""Celery tasks for the ingestion app."""
import logging
from datetime import datetime, timezone

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_weather_data(self, source: str = "open_meteo") -> dict:
    """Fetch raw weather data from an external API and persist an IngestionJob.

    This is a stub implementation. Replace the body with real API client code.

    Args:
        source: Identifier of the data source to pull from.

    Returns:
        A dict with job metadata (id, records_processed, status).
    """
    from apps.ingestion.models import IngestionJob

    logger.info("Starting weather data fetch from source=%s", source)

    job = IngestionJob.objects.create(
        source=source,
        status=IngestionJob.Status.RUNNING,
        started_at=datetime.now(tz=timezone.utc),
    )

    try:
        from apps.ingestion.services import ingest_all_active_stations

        result = ingest_all_active_stations()
        records = result.get("total_records_processed", 0)

        job.status = IngestionJob.Status.SUCCESS
        job.records_processed = records
        job.finished_at = datetime.now(tz=timezone.utc)
        job.save(update_fields=["status", "records_processed", "finished_at", "updated_at"])

        logger.info("Fetch completed: job_id=%s records=%s", job.pk, records)
        return {
            "job_id": job.pk,
            "records_processed": records,
            "status": job.status,
            "details": result,
        }

    except Exception as exc:
        job.status = IngestionJob.Status.FAILED
        job.error_message = str(exc)
        job.finished_at = datetime.now(tz=timezone.utc)
        job.save(update_fields=["status", "error_message", "finished_at", "updated_at"])
        logger.exception("Fetch failed: job_id=%s", job.pk)
        raise self.retry(exc=exc)



@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def process_raw_file(self, file_path: str, job_id: int | None = None) -> dict:
    """Process a raw data file and store observations.

    Args:
        file_path: Absolute path to the file to process.
        job_id: Optional existing IngestionJob primary key to update.

    Returns:
        A dict with processing results.
    """
    logger.info("Processing file: %s (job_id=%s)", file_path, job_id)

    # --- Replace with real file parsing logic ---
    records_processed = 0  # placeholder
    # -------------------------------------------

    return {"file_path": file_path, "records_processed": records_processed}
