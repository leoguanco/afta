from fastapi import FastAPI
from prometheus_client import make_asgi_app
from pydantic import BaseModel

# Now safe to import - chat router no longer imports heavy dependencies
from src.infrastructure.api.endpoints.chat import router as chat_router

app = FastAPI(title="Football Intelligence Engine API", version="0.1.0")

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
    from src.infrastructure.worker.tasks.ingestion_tasks import ingest_match_task
    
    task = ingest_match_task.delay(request.match_id, request.source)
    return {
        "job_id": task.id,
        "status": "PENDING",
        "message": f"Ingestion job started for match {request.match_id}",
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
    # Use send_task to avoid importing vision_tasks (has cv2 dependency)
    task = celery_app.send_task(
        'src.infrastructure.worker.tasks.vision_tasks.process_video_task',
        args=[request.video_path, request.output_path]
    )
    
    return {
        "job_id": task.id,
        "status": "PENDING",
        "message": f"Video processing job started for {request.video_path}",
    }
