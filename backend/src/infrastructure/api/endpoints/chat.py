"""
Chat API Endpoints - Infrastructure Layer

API endpoints for AI analysis chat interface.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.infrastructure.worker.celery_app import celery_app
from src.infrastructure.di.container import Container
import anyio

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
    
    from fastapi.responses import StreamingResponse
    import json
    
    # 1. Build Context (Run sync DB call in thread)
    context_service = Container.get_match_context_service()
    match_context = await anyio.to_thread.run_sync(context_service.build_context, request.match_id)
    
    # 2. Get Adapter
    adapter = Container.get_crewai_adapter()
    

    
    async def event_generator():
        # Yield initial message
        yield f"data: {json.dumps({'type': 'status', 'content': 'Initializing agents...'})}\n\n"
        
        # Run the blocking generator in a thread pool to avoid blocking the event loop
        iterator = adapter.run_analysis_stream(request.match_id, request.query, match_context)
        
        while True:
            try:
                # Retrieve next event in a thread
                event = await anyio.to_thread.run_sync(next, iterator)
                yield f"data: {json.dumps(event)}\n\n"
            except StopIteration:
                break
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
                break

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
