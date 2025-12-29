"""
Celery Application Configuration.

Defines the Celery app and task routing for async workers.
"""

import os
from celery import Celery

# Redis URL from environment or default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "afta_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    # include=[]  # Removed to avoid API importing worker tasks
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "ingestion_tasks.*": {"queue": "default"},
        "vision_tasks.*": {"queue": "gpu_queue"},
        "run_crewai_analysis": {"queue": "default"},
    },
)
