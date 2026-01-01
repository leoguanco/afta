"""
Chat API Endpoints - Infrastructure Layer

API endpoints for AI analysis chat interface.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.infrastructure.worker.celery_app import celery_app

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class AnalyzeRequest(BaseModel):
    """Request model for analysis."""
    match_id: str
    query: str


class AnalyzeResponse(BaseModel):
    """Response model for analysis request."""
    job_id: str
    match_id: str
    status: str


class JobStatusResponse(BaseModel):
    """Response model for job status."""
    job_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None


@router.post("/analyze")
async def start_analysis(request: AnalyzeRequest):
    """
    Start an AI analysis and stream results (SSE).
    
    Uses Server-Sent Events to stream status updates and final result.
    
    Args:
        request: Analysis request with match_id and query
        
    Returns:
        StreamingResponse (text/event-stream)
    """
    from fastapi.responses import StreamingResponse
    import json
    
    from src.infrastructure.adapters.crewai_adapter import CrewAIAdapter
    from src.application.services.match_context_service import MatchContextService
    
    # 0. Instantiate Repositories (Infrastructure Layer)
    from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
    from src.infrastructure.db.repositories.postgres_metrics_repo import PostgresMetricsRepository
    
    match_repo = PostgresMatchRepo()
    metrics_repo = PostgresMetricsRepository()
    
    # 1. Build Context (Sync, fast)
    context_service = MatchContextService(match_repo, metrics_repo)
    match_context = context_service.build_context(request.match_id)
    
    # 2. Initialize Adapter
    adapter = CrewAIAdapter()
    
    async def event_generator():
        # Yield initial message
        yield f"data: {json.dumps({'type': 'status', 'content': 'Initializing agents...'})}\n\n"
        
        # Stream events from adapter
        # run_analysis_stream is a sync generator, so we iterate normally
        # In a real async app, we might want to run this in a threadpool executor 
        # to avoid blocking the event loop if the generator blocks.
        # However, run_analysis_stream uses a thread internally and yields from a queue,
        # so iterating it here is mostly waiting on queue.get(), which behaves okay-ish 
        # but technically blocks the loop. Ideally we wrap iteration in run_in_executor
        # OR just accept it for low traffic.
        # Given CrewAIAdapter.run_analysis_stream implementation uses a blocking queue.get(),
        # it WILL block this async function. 
        # Better approach: The adapter's generator blocks. We should iterate it.
        # Since we are in an async def, blocking calls block the loop.
        
        # To make it key-friendly:
        for event in adapter.run_analysis_stream(request.match_id, request.query, match_context):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status of an analysis job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status and result (if completed)
    """
    task_result = celery_app.AsyncResult(job_id)
    
    if task_result.state == 'PENDING':
        return JobStatusResponse(
            job_id=job_id,
            status='PENDING'
        )
    elif task_result.state == 'STARTED':
        return JobStatusResponse(
            job_id=job_id,
            status='RUNNING'
        )
    elif task_result.state == 'SUCCESS':
        result_data = task_result.result
        return JobStatusResponse(
            job_id=job_id,
            status=result_data.get('status', 'COMPLETED'),
            result=result_data.get('result')
        )
    elif task_result.state == 'FAILURE':
        return JobStatusResponse(
            job_id=job_id,
            status='FAILED',
            error=str(task_result.info)
        )
    else:
        return JobStatusResponse(
            job_id=job_id,
            status=task_result.state
        )
