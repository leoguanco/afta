"""
Process Video Use Case.

Application layer orchestrator that triggers async video processing jobs.
"""

from dataclasses import dataclass
from typing import Optional
from src.infrastructure.worker.tasks.vision_tasks import process_video_task


@dataclass
class VideoJobResult:
    """Result of starting a video processing job."""

    job_id: str
    status: str
    message: Optional[str] = None


class ProcessVideoUseCase:
    """
    Use Case to start an async video processing job.

    Dispatches a Celery task to the GPU queue and returns the job ID immediately.
    """

    def execute(self, video_path: str, output_path: str) -> VideoJobResult:
        """
        Start a video processing job.

        Args:
            video_path: Path to the input video file.
            output_path: Path to save the trajectory output.

        Returns:
            VideoJobResult with the task ID.
        """
        # Dispatch Celery task to GPU queue
        task = process_video_task.delay(video_path, output_path)

        return VideoJobResult(
            job_id=task.id,
            status="PENDING",
            message=f"Video processing job started for {video_path}",
        )
