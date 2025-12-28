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


@router.post("/analyze", response_model=AnalyzeResponse)
async def start_analysis(request: AnalyzeRequest):
    """
    Start an AI analysis job.
    
    Dispatches analysis to Celery worker (where CrewAI dependencies exist).
    
    Args:
        request: Analysis request with match_id and query
        
    Returns:
        Job information with job_id for status polling
    """
    # Use Case: MatchAnalyzer
    from src.infrastructure.adapters.celery_analysis_dispatcher import CeleryAnalysisDispatcher
    from src.application.use_cases.match_analyzer import MatchAnalyzer
    
    dispatcher = CeleryAnalysisDispatcher()
    use_case = MatchAnalyzer(dispatcher)
    
    result = use_case.execute(request.match_id, request.query)
    
    return AnalyzeResponse(
        job_id=result.job_id,
        match_id=result.match_id,
        status=result.status
    )


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
