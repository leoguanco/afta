"""
Video API Endpoints - Infrastructure Layer

Endpoints for video processing and calibration.
"""
from typing import Optional, Literal
from fastapi import APIRouter
from pydantic import BaseModel

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
