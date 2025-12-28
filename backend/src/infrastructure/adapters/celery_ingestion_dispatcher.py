"""
CeleryIngestionDispatcher - Infrastructure Adapter
"""
from src.domain.ports.ingestion_port import IngestionPort
from src.infrastructure.worker.celery_app import celery_app

class CeleryIngestionDispatcher(IngestionPort):
    def start_ingestion(self, match_id: str, source: str) -> str:
        task = celery_app.send_task(
            'src.infrastructure.worker.tasks.ingestion_tasks.ingest_match_task',
            args=[match_id, source]
        )
        return task.id
