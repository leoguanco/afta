"""
Pattern Detection API Endpoints - Infrastructure Layer

Endpoints for tactical pattern detection and querying.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from src.infrastructure.worker.celery_app import celery_app

router = APIRouter(prefix="/api/v1", tags=["patterns"])


class DetectPatternsRequest(BaseModel):
    """Request body for pattern detection."""
    match_id: str
    team_id: str = "home"
    n_clusters: int = 8


class DetectPatternsResponse(BaseModel):
    """Response for pattern detection request."""
    job_id: str
    match_id: str
    status: str = "PENDING"
    message: str


@router.post("/patterns/detect", response_model=DetectPatternsResponse)
async def detect_patterns(request: DetectPatternsRequest):
    """
    Start pattern detection job.
    
    Dispatches to Celery worker for async processing.
    Uses K-means clustering to discover tactical patterns from possession sequences.
    """
    task = celery_app.send_task(
        'detect_tactical_patterns',
        args=[request.match_id, request.team_id, request.n_clusters]
    )
    
    return DetectPatternsResponse(
        job_id=task.id,
        match_id=request.match_id,
        status="PENDING",
        message=f"Pattern detection started for match {request.match_id}"
    )


@router.get("/patterns/jobs/{job_id}")
async def get_pattern_job_status(job_id: str):
    """
    Get the status of a pattern detection job.
    """
    task_result = celery_app.AsyncResult(job_id)
    
    if task_result.state == 'PENDING':
        return {"job_id": job_id, "status": "PENDING"}
    elif task_result.state == 'STARTED':
        return {"job_id": job_id, "status": "RUNNING"}
    elif task_result.state == 'SUCCESS':
        result = task_result.result
        return {
            "job_id": job_id,
            "status": "COMPLETED",
            "pattern_count": result.get("pattern_count"),
            "sequence_count": result.get("sequence_count"),
            "patterns": result.get("patterns", [])
        }
    elif task_result.state == 'FAILURE':
        return {
            "job_id": job_id,
            "status": "FAILED",
            "error": str(task_result.info)
        }
    else:
        return {"job_id": job_id, "status": task_result.state}


@router.get("/matches/{match_id}/patterns")
async def get_match_patterns(match_id: str, team_id: str = "home"):
    """
    Get discovered patterns for a match.
    
    Returns patterns if pattern detection has been run, empty list otherwise.
    """
    # For now, run synchronously for GET requests
    # In production, this would query the pattern repository
    try:
        from src.application.use_cases.pattern_detector import PatternDetector
        from src.infrastructure.ml.sklearn_pattern_detector import SklearnPatternDetector
        from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
        
        detector = SklearnPatternDetector()
        match_repo = PostgresMatchRepo()
        
        use_case = PatternDetector(
            detector=detector,
            match_repository=match_repo
        )
        
        result = use_case.execute(match_id=match_id, team_id=team_id)
        
        return {
            "match_id": match_id,
            "team_id": team_id,
            "pattern_count": result.pattern_count,
            "sequence_count": result.sequence_count,
            "patterns": [p.to_dict() for p in result.patterns]
        }
    except Exception as e:
        return {
            "match_id": match_id,
            "team_id": team_id,
            "pattern_count": 0,
            "error": str(e)
        }


@router.get("/patterns/{pattern_id}/examples")
async def get_pattern_examples(pattern_id: str, limit: int = 10):
    """
    Get example sequences for a pattern.
    
    Returns sequence IDs that belong to this pattern cluster.
    """
    # Placeholder - would query pattern repository
    return {
        "pattern_id": pattern_id,
        "examples": [],
        "message": "Pattern examples require running pattern detection first"
    }
