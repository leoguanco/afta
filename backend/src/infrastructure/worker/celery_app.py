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
    task_default_queue="default",
    task_routes={
        "src.infrastructure.worker.tasks.ingestion_tasks.*": {"queue": "default"},
        "src.infrastructure.worker.tasks.vision_tasks.*": {"queue": "gpu_queue"},
        "src.infrastructure.worker.tasks.crewai_tasks.*": {"queue": "default"},
        "run_crewai_analysis": {"queue": "default"},
    },
)
