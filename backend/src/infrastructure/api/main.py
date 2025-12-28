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
    return {"status": "ok", "db": "unknown", "redis": "unknown"}


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
