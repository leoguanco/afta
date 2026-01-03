"""
Ingestion Tasks (Celery Workers).

Background tasks for data ingestion, routed to the CPU worker queue.
"""

import logging
from src.infrastructure.worker.celery_app import celery_app
from src.infrastructure.adapters.statsbomb_adapter import StatsBombAdapter
from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
from src.infrastructure.di.container import Container

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

        # Save to database using PostgresMatchRepo
        repo = PostgresMatchRepo()
        repo.save(match)

        logger.info(f"Ingestion complete: {len(match.events)} events")

        # --- RAG Indexing ---
        try:
            indexer = Container.get_match_data_indexer()
            # Convert events to dict format for indexing
            events_for_indexing = [
                {
                    "type": e.event_type.value,
                    "player": e.player_id,
                    "team": e.team_id,
                    "minute": int(e.timestamp / 60) if e.timestamp else 0,
                }
                for e in match.events
            ]
            index_result = indexer.execute(
                match_id=match.match_id,
                match_events=events_for_indexing
            )
            logger.info(f"RAG indexed {index_result.documents_indexed} documents")
        except Exception as index_err:
            # Don't fail ingestion if indexing fails
            logger.warning(f"RAG indexing failed (non-critical): {index_err}")

        return {
            "status": "success",
            "match_id": match.match_id,
            "event_count": len(match.events),
        }

    except Exception as exc:
        logger.error(f"Ingestion failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2**self.request.retries)

