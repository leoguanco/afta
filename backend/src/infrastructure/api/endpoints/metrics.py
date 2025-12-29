"""
Metrics API Endpoints - Infrastructure Layer

Endpoints for tactical metrics calculation.
"""
from fastapi import APIRouter
from pydantic import BaseModel

from src.infrastructure.worker.celery_app import celery_app

router = APIRouter(prefix="/api/v1", tags=["metrics"])


class MetricsRequest(BaseModel):
    """Request body for metrics calculation endpoint."""
    match_id: str
    tracking_data: list = []  # Optional - will fetch from storage if empty
    event_data: list = []


@router.post("/calculate-metrics")
async def calculate_metrics(request: MetricsRequest):
    """
    Start an async tactical metrics calculation job.
    
    Calculates distances, speeds, pitch control, PPDA, etc.
    If tracking_data is empty, fetches from storage.
    
    Returns immediately with a job_id for status polling.
    """
    task = celery_app.send_task(
        'calculate_match_metrics',  # Uses shared_task name
        args=[request.match_id, request.tracking_data, request.event_data]
    )
    
    return {
        "job_id": task.id,
        "status": "PENDING",
        "message": f"Metrics calculation started for match {request.match_id}",
    }
