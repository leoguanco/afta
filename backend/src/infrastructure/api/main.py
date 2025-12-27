from fastapi import FastAPI
from prometheus_client import make_asgi_app
from pydantic import BaseModel

from src.application.use_cases.start_ingestion import StartIngestionUseCase

app = FastAPI(title="Football Intelligence Engine API", version="0.1.0")

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

    Returns immediately with a job_id that can be polled for status.
    """
    use_case = StartIngestionUseCase()
    result = use_case.execute(request.match_id, request.source)
    return {
        "job_id": result.job_id,
        "status": result.status,
        "message": result.message,
    }
