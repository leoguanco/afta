"""
Video API Endpoints - Infrastructure Layer

Endpoints for video processing and calibration.
"""
import logging
from typing import Optional, Literal
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["video"])


class MatchMetadata(BaseModel):
    """Optional match metadata for video uploads."""
    home_team: str = "Home"
    away_team: str = "Away"
    date: Optional[str] = None
    competition: Optional[str] = None


class VideoProcessRequest(BaseModel):
    """Request body for video processing endpoint."""
    video_path: str
    output_path: str
    metadata: Optional[MatchMetadata] = None
    sync_offset_seconds: float = 0.0
    mode: Literal["full_match", "highlights"] = "full_match"


class CalibrationRequest(BaseModel):
    """Request body for pitch calibration endpoint."""
    video_id: str
    keypoints: list  # List of {"pixel_x", "pixel_y", "pitch_x", "pitch_y", "name"?}


@router.post("/process-video")
async def process_video(request: VideoProcessRequest):
    """
    Start an async video processing job (GPU worker).
    
    This endpoint dispatches to the GPU worker which runs:
    - YOLO object detection
    - ByteTrack multi-object tracking
    - Trajectory extraction
    
    Returns immediately with a job_id for status polling.
    """
    from src.infrastructure.adapters.celery_video_dispatcher import CeleryVideoDispatcher
    from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
    from src.application.use_cases.video_processor import VideoProcessor
    
    dispatcher = CeleryVideoDispatcher()
    match_repo = PostgresMatchRepo()
    
    use_case = VideoProcessor(dispatcher, match_repo)
    
    # Convert MatchMetadata to dict if provided
    metadata_dict = None
    if request.metadata:
        metadata_dict = {
            "home_team": request.metadata.home_team,
            "away_team": request.metadata.away_team,
            "date": request.metadata.date,
            "competition": request.metadata.competition,
        }
    
    result = use_case.execute(
        video_path=request.video_path, 
        output_path=request.output_path,
        metadata=metadata_dict,
        sync_offset_seconds=request.sync_offset_seconds,
        mode=request.mode
    )
    
    return {
        "job_id": result.job_id,
        "status": result.status,
        "message": result.message,
    }


@router.post("/calibrate")
async def calibrate_video(request: CalibrationRequest):
    """
    Start an async pitch calibration job.
    
    Computes homography matrix from pixel-to-pitch keypoint correspondences.
    Requires at least 4 keypoints (pitch corners or line intersections).
    
    Returns immediately with a job_id for status polling.
    """
    from src.infrastructure.adapters.celery_calibration_dispatcher import CeleryCalibrationDispatcher
    from src.application.use_cases.video_calibrator import VideoCalibrator
    
    dispatcher = CeleryCalibrationDispatcher()
    use_case = VideoCalibrator(dispatcher)
    
    result = use_case.execute(request.video_id, request.keypoints)
    
    return {
        "job_id": result.job_id,
        "status": result.status,
        "message": result.message,
    }


@router.post("/video/upload")
async def upload_video(
    file: UploadFile = File(...),
    home_team: str = Form("Home"),
    away_team: str = Form("Away"),
    date: Optional[str] = Form(None),
    competition: Optional[str] = Form(None),
    mode: Literal["full_match", "highlights"] = Form("full_match"),
    auto_process: bool = Form(True),
):
    """
    Upload a video file for processing.
    
    Accepts video file upload via multipart form data.
    Stores the file in MinIO and optionally triggers processing.
    
    Args:
        file: The video file to upload
        home_team: Name of the home team
        away_team: Name of the away team  
        date: Match date (optional)
        competition: Competition name (optional)
        auto_process: Whether to automatically start processing after upload
    
    Returns:
        Upload result with file key and optional job_id
    """
    from fastapi.responses import JSONResponse
    import uuid
    
    from src.infrastructure.storage.minio_adapter import MinIOAdapter
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("video/"):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Invalid file type",
                "message": "Only video files are accepted",
                "content_type": file.content_type
            }
        )
    
    # Generate unique ID for this upload
    upload_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1] if file.filename and "." in file.filename else "mp4"
    file_key = f"uploads/{upload_id}.{file_extension}"
    
    try:
        # Initialize MinIO client with videos bucket
        storage = MinIOAdapter(bucket="videos")
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Check file size (max 2GB)
        max_size = 2 * 1024 * 1024 * 1024  # 2GB
        if file_size > max_size:
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "File too large",
                    "message": f"Maximum file size is 2GB. Your file is {file_size / (1024*1024*1024):.2f}GB"
                }
            )
        
        # Store in MinIO
        storage.put_object(file_key, content, content_type=file.content_type or "video/mp4")
        
        logger.info(f"Uploaded video to MinIO: {file_key} ({file_size} bytes)")
        
        result = {
            "upload_id": upload_id,
            "file_key": file_key,
            "file_size": file_size,
            "filename": file.filename,
            "status": "uploaded",
        }
        
        # Auto-process if requested
        if auto_process:
            from src.infrastructure.adapters.celery_video_dispatcher import CeleryVideoDispatcher
            from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
            from src.application.use_cases.video_processor import VideoProcessor
            
            dispatcher = CeleryVideoDispatcher()
            match_repo = PostgresMatchRepo()
            use_case = VideoProcessor(dispatcher, match_repo)
            
            # Get MinIO internal path for processing
            # The worker needs the MinIO path format
            video_path = f"minio://videos/{file_key}"
            output_path = f"matches/{upload_id}"
            
            process_result = use_case.execute(
                video_path=video_path,
                output_path=output_path,
                metadata={
                    "home_team": home_team,
                    "away_team": away_team,
                    "date": date,
                    "competition": competition,
                },
                sync_offset_seconds=0.0,
                mode=mode
            )
            
            result["job_id"] = process_result.job_id
            result["status"] = "processing"
            result["match_id"] = upload_id
            
            logger.info(f"Started processing job {process_result.job_id} for upload {upload_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Video upload failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Upload failed",
                "message": str(e)
            }
        )


@router.get("/video/job/{job_id}")
async def get_video_job_status(job_id: str):
    """
    Get the status of a video processing job.
    
    Returns current status, progress, and result when complete.
    """
    from src.infrastructure.worker.celery_app import celery_app
    
    task_result = celery_app.AsyncResult(job_id)
    
    # Map Celery states to user-friendly statuses
    status_map = {
        'PENDING': 'queued',
        'STARTED': 'processing', 
        'PROGRESS': 'processing',
        'SUCCESS': 'completed',
        'FAILURE': 'failed',
        'REVOKED': 'cancelled',
    }
    
    status = status_map.get(task_result.state, task_result.state.lower())
    
    response = {
        "job_id": job_id,
        "status": status,
        "state": task_result.state,
    }
    
    # Add progress info if available
    if task_result.state == 'PROGRESS' and task_result.info:
        response["progress"] = task_result.info.get("progress", 0)
        response["message"] = task_result.info.get("message", "Processing...")
    elif task_result.state == 'SUCCESS':
        result_data = task_result.result or {}
        response["match_id"] = result_data.get("match_id")
        response["message"] = result_data.get("message", "Processing complete")
    elif task_result.state == 'FAILURE':
        response["error"] = str(task_result.info)
        response["message"] = "Processing failed"
    elif task_result.state == 'PENDING':
        response["message"] = "Waiting in queue..."
    elif task_result.state == 'STARTED':
        response["message"] = "Processing started..."
    
    return response


@router.get("/video/{match_id}/stream")
async def stream_video(match_id: str):
    """
    Stream the processed video file for a match.
    
    Returns the video file from MinIO storage.
    The video is stored after processing via /process-video endpoint.
    """
    from fastapi import Request, HTTPException
    from fastapi.responses import StreamingResponse, JSONResponse
    from minio.error import S3Error
    import io
    
    from src.infrastructure.storage.minio_adapter import MinIOAdapter
    
    try:
        # Initialize MinIO client with video bucket
        storage = MinIOAdapter(bucket="videos")
        
        # Video is stored at matches/{match_id}/output.mp4 after processing
        video_key = f"matches/{match_id}/output.mp4"
        
        try:
            # Check if object exists by trying to stat it
            stat = storage.client.stat_object(storage.bucket, video_key)
            content_length = stat.size
            content_type = stat.content_type or "video/mp4"
            
        except S3Error as e:
            if e.code == "NoSuchKey" or e.code == "NoSuchBucket":
                return JSONResponse(
                    status_code=404,
                    content={
                        "detail": "Video not found",
                        "message": f"No processed video exists for match '{match_id}'.",
                        "match_id": match_id,
                        "hint": "Process a video first using POST /api/v1/process-video"
                    }
                )
            raise
        
        # Stream the video file
        def generate():
            try:
                response = storage.client.get_object(storage.bucket, video_key)
                for chunk in response.stream(32 * 1024):  # 32KB chunks
                    yield chunk
                response.close()
                response.release_conn()
            except Exception as e:
                logger.error(f"Error streaming video: {e}")
        
        return StreamingResponse(
            generate(),
            media_type=content_type,
            headers={
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
                "Content-Disposition": f'inline; filename="{match_id}.mp4"',
            }
        )
        
    except Exception as e:
        logger.error(f"Video streaming error for {match_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Video streaming error",
                "message": str(e),
                "match_id": match_id
            }
        )
