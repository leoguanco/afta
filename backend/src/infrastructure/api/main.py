import os
import uuid
from fastapi import FastAPI, Request
from prometheus_client import make_asgi_app
from pydantic import BaseModel

# Configure JSON logging
from src.infrastructure.logging import configure_logging, set_correlation_id, get_logger

# Use JSON format in production (when not in DEBUG mode)
use_json = os.getenv("DEBUG", "false").lower() != "true"
configure_logging(json_format=use_json)

logger = get_logger(__name__)

# Celery app for task dispatch
from src.infrastructure.worker.celery_app import celery_app

# Now safe to import - chat router no longer imports heavy dependencies
from src.infrastructure.api.endpoints.chat import router as chat_router

app = FastAPI(title="Football Intelligence Engine API", version="0.1.0")


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Add correlation ID to each request for tracing."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4())[:8])
    set_correlation_id(correlation_id)
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


# Register routers
app.include_router(chat_router)

# Observability
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)



class IngestionRequest(BaseModel):
    """Request body for ingestion endpoint."""
    source: str
    match_id: str


@app.get("/")
async def root():
    return {"message": "Welcome to AFTA API", "system": "operational"}


@app.get("/health")
async def health():
    """Health check endpoint with real connectivity tests."""
    health_status = {"status": "ok"}
    
    # Check database connectivity
    try:
        from src.infrastructure.db.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["db"] = "ok"
    except Exception as e:
        health_status["db"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis connectivity
    try:
        from redis import Redis
        import os
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = Redis.from_url(redis_url, socket_connect_timeout=2)
        redis_client.ping()
        health_status["redis"] = "ok"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@app.post("/api/v1/ingest")
async def start_ingestion(request: IngestionRequest):
    """
    Start an async ingestion job.

    Dispatches to Celery worker (where heavy dependencies exist).
    """
    # Use Case: MatchIngester
    from src.infrastructure.adapters.celery_ingestion_dispatcher import CeleryIngestionDispatcher
    from src.application.use_cases.match_ingester import MatchIngester
    
    dispatcher = CeleryIngestionDispatcher()
    use_case = MatchIngester(dispatcher)
    
    result = use_case.execute(request.match_id, request.source)
    return {
        "job_id": result.job_id,
        "status": result.status,
        "message": result.message,
    }


class VideoProcessRequest(BaseModel):
    """Request body for video processing endpoint."""
    video_path: str
    output_path: str


@app.post("/api/v1/process-video")
async def process_video(request: VideoProcessRequest):
    """
    Start an async video processing job (GPU worker).
    
    This endpoint dispatches to the GPU worker which runs:
    - YOLO object detection
    - ByteTrack multi-object tracking
    - Trajectory extraction
    
    Returns immediately with a job_id for status polling.
    """
    # Use Case: VideoProcessor
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


class CalibrationRequest(BaseModel):
    """Request body for pitch calibration endpoint."""
    video_id: str
    keypoints: list  # List of {"pixel_x", "pixel_y", "pitch_x", "pitch_y", "name"?}


@app.post("/api/v1/calibrate")
async def calibrate_video(request: CalibrationRequest):
    """
    Start an async pitch calibration job.
    
    Computes homography matrix from pixel-to-pitch keypoint correspondences.
    Requires at least 4 keypoints (pitch corners or line intersections).
    
    Returns immediately with a job_id for status polling.
    """
    # Use Case: VideoCalibrator
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


class MetricsRequest(BaseModel):
    """Request body for metrics calculation endpoint."""
    match_id: str
    tracking_data: list = []  # Optional - will fetch from storage if empty
    event_data: list = []


@app.post("/api/v1/calculate-metrics")
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


# =============================================================================
# Phase Classification Endpoints
# =============================================================================

class PhaseClassificationRequest(BaseModel):
    """Request body for phase classification endpoint."""
    match_id: str
    team_id: str = "home"  # Perspective: home or away


@app.post("/api/v1/matches/{match_id}/classify-phases")
async def classify_match_phases(match_id: str, request: PhaseClassificationRequest = None):
    """
    Start an async phase classification job.
    
    Classifies each frame of tracking data into one of 4 game phases:
    - ORGANIZED_ATTACK
    - ORGANIZED_DEFENSE
    - TRANSITION_ATK_DEF
    - TRANSITION_DEF_ATK
    
    Requires a trained ML model to be available.
    
    Returns immediately with a job_id for status polling.
    """
    team_id = request.team_id if request else "home"
    
    task = celery_app.send_task(
        'classify_match_phases',  # Uses shared_task name
        args=[match_id, team_id]
    )
    
    return {
        "job_id": task.id,
        "status": "PENDING",
        "message": f"Phase classification started for match {match_id}",
    }


class PhaseQueryParams(BaseModel):
    """Query parameters for phase retrieval."""
    start_frame: int = 0
    end_frame: int = None


@app.get("/api/v1/matches/{match_id}/phases")
async def get_match_phases(
    match_id: str,
    start_frame: int = 0,
    end_frame: int = None,
    team_id: str = "home"
):
    """
    Get classified phases for a match.
    
    Returns phase labels, transitions, and statistics for the specified frame range.
    
    Query params:
    - start_frame: First frame to include (default: 0)
    - end_frame: Last frame to include (default: all)
    - team_id: Perspective (home/away)
    """
    from src.infrastructure.storage.phase_repository import phase_repository
    
    # Check if classification exists
    if not phase_repository.has_classification(match_id, team_id):
        return {
            "match_id": match_id,
            "team_id": team_id,
            "status": "not_classified",
            "message": "Phase data not yet available. Run classify-phases first.",
            "phases": [],
            "statistics": {
                "transition_count": 0,
                "phase_percentages": {}
            }
        }
    
    # Get statistics (fast, uses precomputed values)
    stats = phase_repository.get_statistics(match_id, team_id)
    
    # Get phases in range
    phases = phase_repository.get_phases_in_range(match_id, team_id, start_frame, end_frame)
    
    return {
        "match_id": match_id,
        "team_id": team_id,
        "status": "classified",
        "total_frames": stats.get("total_frames", 0),
        "phases": phases,
        "statistics": {
            "transition_count": stats.get("transition_count", 0),
            "phase_percentages": stats.get("phase_percentages", {}),
            "dominant_phase": stats.get("dominant_phase", "unknown")
        }
    }


@app.get("/api/v1/matches/{match_id}/phases/transitions")
async def get_phase_transitions(match_id: str, team_id: str = "home"):
    """
    Get all phase transitions for a match.
    
    Returns list of transition events with frame numbers and timestamps.
    Useful for identifying key moments in the match.
    """
    from src.infrastructure.storage.phase_repository import phase_repository
    
    # Check if classification exists
    if not phase_repository.has_classification(match_id, team_id):
        return {
            "match_id": match_id,
            "team_id": team_id,
            "transitions": [],
            "message": "Run classify-phases first to generate transitions."
        }
    
    # Get transitions
    transitions = phase_repository.get_transitions(match_id, team_id)
    
    return {
        "match_id": match_id,
        "team_id": team_id,
        "transition_count": len(transitions),
        "transitions": [
            {
                "frame_id": t.frame_id,
                "timestamp": t.timestamp,
                "from_phase": t.from_phase.value,
                "to_phase": t.to_phase.value
            }
            for t in transitions
        ]
    }


class TrainClassifierRequest(BaseModel):
    """Request body for classifier training."""
    training_data_path: str
    model_name: str = "phase_classifier"


@app.post("/api/v1/classifiers/phase/train")
async def train_phase_classifier(request: TrainClassifierRequest):
    """
    Start training the phase classifier model.
    
    Requires labeled training data with features and phase labels.
    The trained model will be saved for future classification jobs.
    """
    task = celery_app.send_task(
        'train_phase_classifier',
        args=[request.training_data_path, f"/app/models/{request.model_name}.joblib"]
    )
    
    return {
        "job_id": task.id,
        "status": "PENDING",
        "message": f"Classifier training started from {request.training_data_path}",
    }

