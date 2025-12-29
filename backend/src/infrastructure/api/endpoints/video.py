"""
Video API Endpoints - Infrastructure Layer

Endpoints for video processing and calibration.
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["video"])


class VideoProcessRequest(BaseModel):
    """Request body for video processing endpoint."""
    video_path: str
    output_path: str


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
    from src.application.use_cases.video_processor import VideoProcessor
    
    dispatcher = CeleryVideoDispatcher()
    use_case = VideoProcessor(dispatcher)
    
    result = use_case.execute(request.video_path, request.output_path)
    
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
