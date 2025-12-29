"""
FastAPI Main Application - Infrastructure Layer

Minimal main.py that only handles:
- App initialization
- Middleware
- Router registration
- Health checks
"""
import os
import uuid
from fastapi import FastAPI, Request
from prometheus_client import make_asgi_app

# Configure JSON logging
from src.infrastructure.logging import configure_logging, set_correlation_id, get_logger

# Use JSON format in production (when not in DEBUG mode)
use_json = os.getenv("DEBUG", "false").lower() != "true"
configure_logging(json_format=use_json)

logger = get_logger(__name__)

# Import routers
from src.infrastructure.api.endpoints.chat import router as chat_router
from src.infrastructure.api.endpoints.reports import router as reports_router
from src.infrastructure.api.endpoints.ingestion import router as ingestion_router
from src.infrastructure.api.endpoints.video import router as video_router
from src.infrastructure.api.endpoints.metrics import router as metrics_router
from src.infrastructure.api.endpoints.phases import router as phases_router

app = FastAPI(title="Football Intelligence Engine API", version="0.1.0")


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Add correlation ID to each request for tracing."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4())[:8])
    set_correlation_id(correlation_id)
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


# =============================================================================
# Register Routers
# =============================================================================
app.include_router(chat_router)
app.include_router(reports_router)
app.include_router(ingestion_router)
app.include_router(video_router)
app.include_router(metrics_router)
app.include_router(phases_router)

# Observability
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# =============================================================================
# Core Endpoints (kept in main.py)
# =============================================================================

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
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = Redis.from_url(redis_url, socket_connect_timeout=2)
        redis_client.ping()
        health_status["redis"] = "ok"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status
