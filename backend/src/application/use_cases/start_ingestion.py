"""
Start Ingestion Use Case.

Application layer orchestrator that triggers async ingestion jobs.
"""

from dataclasses import dataclass
from typing import Optional
from src.infrastructure.worker.tasks.ingestion_tasks import ingest_match_task


@dataclass
class IngestionJobResult:
    """Result of starting an ingestion job."""

    job_id: str
    status: str
    message: Optional[str] = None


class StartIngestionUseCase:
    """
    Use Case to start an async ingestion job.

    Dispatches a Celery task and returns the job ID immediately.
    """

    def execute(self, match_id: str, source: str) -> IngestionJobResult:
        """
        Start an ingestion job.

        Args:
            match_id: The match ID to ingest.
            source: Data source ("statsbomb", "metrica").

        Returns:
            IngestionJobResult with the task ID.
        """
        # Dispatch Celery task
        task = ingest_match_task.delay(match_id, source)

        return IngestionJobResult(
            job_id=task.id,
            status="PENDING",
            message=f"Ingestion job started for match {match_id}",
        )
