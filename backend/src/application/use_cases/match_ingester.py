"""
MatchIngester - Application Layer
"""
from dataclasses import dataclass
from typing import Optional
from src.domain.ports.ingestion_port import IngestionPort

@dataclass
class IngestionJobResult:
    job_id: str
    status: str
    message: Optional[str] = None

class MatchIngester:
    def __init__(self, dispatcher: IngestionPort):
        self.dispatcher = dispatcher
        
    def execute(self, match_id: str, source: str) -> IngestionJobResult:
        job_id = self.dispatcher.start_ingestion(match_id, source)
        return IngestionJobResult(
            job_id=job_id,
            status="PENDING",
            message=f"Ingestion job started for match {match_id}"
        )
