"""
Video API Endpoints - Infrastructure Layer

Endpoints for video processing and calibration.
"""
import logging
from typing import Optional, Literal
from fastapi import APIRouter
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
