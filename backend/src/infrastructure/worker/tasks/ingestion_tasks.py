"""
Ingestion Tasks (Celery Workers).

Background tasks for data ingestion, routed to the CPU worker queue.
"""

import logging
from src.infrastructure.worker.celery_app import celery_app
from src.infrastructure.adapters.statsbomb_adapter import StatsBombAdapter

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, queue="default", max_retries=3)
def ingest_match_task(self, match_id: str, source: str) -> dict:
    """
    Background task to ingest a match from an external source.

    Args:
        match_id: The match ID to ingest.
        source: Data source ("statsbomb", "metrica").

    Returns:
        Dict with status and event count.
    """
    try:
        logger.info(f"Starting ingestion for match {match_id} from {source}")

        # Select adapter based on source
        if source == "statsbomb":
            adapter = StatsBombAdapter()
        else:
            raise ValueError(f"Unknown source: {source}")

        # Fetch and transform match data
        match = adapter.get_match(match_id, source)

        if match is None:
            return {"status": "error", "message": f"Match {match_id} not found"}

        # TODO: Save to database using PostgresMatchRepo

        logger.info(f"Ingestion complete: {len(match.events)} events")

        return {
            "status": "success",
            "match_id": match.match_id,
            "event_count": len(match.events),
        }

    except Exception as exc:
        logger.error(f"Ingestion failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2**self.request.retries)
