"""
Report API Endpoints - Infrastructure Layer

API endpoints for tactical report generation and download.
"""
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional

from src.infrastructure.worker.celery_app import celery_app

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


class GenerateReportRequest(BaseModel):
    """Request body for report generation."""
    match_id: str
    team_id: str = "home"
    format: str = "pdf"  # "pdf" or "json"
    include_ai_analysis: bool = True
    include_charts: bool = True
    title: Optional[str] = None


class GenerateReportResponse(BaseModel):
    """Response for report generation request."""
    job_id: str
    match_id: str
    status: str = "PENDING"
    message: str


@router.post("/generate", response_model=GenerateReportResponse)
async def generate_report(request: GenerateReportRequest):
    """
    Start report generation job.
    
    Dispatches to Celery worker for async processing.
    Returns job ID for status polling.
    """
    # Dispatch to Celery
    task = celery_app.send_task(
        'generate_tactical_report',
        args=[
            request.match_id,
            request.team_id,
            request.format,
            request.include_ai_analysis,
            request.include_charts,
            request.title
        ]
    )
    
    return GenerateReportResponse(
        job_id=task.id,
        match_id=request.match_id,
        status="PENDING",
        message=f"Report generation started for match {request.match_id}"
    )


@router.get("/jobs/{job_id}")
async def get_report_job_status(job_id: str):
    """
    Get the status of a report generation job.
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
            "report_id": result.get("report_id"),
            "filename": result.get("filename"),
            "download_url": f"/api/v1/reports/{result.get('report_id')}/download"
        }
    elif task_result.state == 'FAILURE':
        return {
            "job_id": job_id,
            "status": "FAILED",
            "error": str(task_result.info)
        }
    else:
        return {"job_id": job_id, "status": task_result.state}


@router.get("/{report_id}/download")
async def download_report(report_id: str):
    """
    Download a generated report.
    
    Retrieves from MinIO storage.
    """
    try:
        # Lazy import to avoid loading heavy dependencies
        from src.infrastructure.storage.minio_adapter import MinIOAdapter
        
        storage = MinIOAdapter()
        
        # Try PDF first, then JSON
        for ext in ['pdf', 'json']:
            try:
                key = f"reports/{report_id}.{ext}"
                content = storage.get_object(key)
                
                media_type = "application/pdf" if ext == "pdf" else "application/json"
                filename = f"report_{report_id}.{ext}"
                
                return Response(
                    content=content,
                    media_type=media_type,
                    headers={
                        "Content-Disposition": f"attachment; filename={filename}"
                    }
                )
            except Exception:
                continue
        
        raise HTTPException(status_code=404, detail="Report not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
