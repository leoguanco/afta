"""
Ingestion API Endpoints - Infrastructure Layer

Endpoints for match data ingestion.
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["ingestion"])


class IngestionRequest(BaseModel):
    """Request body for ingestion endpoint."""
    source: str
    match_id: str


@router.post("/ingest")
async def start_ingestion(request: IngestionRequest):
    """
    Start an async ingestion job.

    Dispatches to Celery worker (where heavy dependencies exist).
    """
    from src.infrastructure.adapters.celery_ingestion_dispatcher import CeleryIngestionDispatcher
    from src.application.use_cases.match_ingester import MatchIngester
    
    dispatcher = CeleryIngestionDispatcher()
    use_case = MatchIngester(dispatcher)
    
    result = use_case.execute(request.match_id, request.source)
    return {
        "job_id": result.job_id,
        "status": result.status,
        "message": result.message,
    }
