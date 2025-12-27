"""
Start Calibration Use Case.

Application layer orchestrator that triggers async calibration jobs.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.infrastructure.worker.tasks.calibration_tasks import calibrate_video_task


@dataclass
class CalibrationJobResult:
    """Result of starting a calibration job."""

    job_id: str
    status: str
    message: Optional[str] = None


class StartCalibrationUseCase:
    """
    Use Case to start an async calibration job.

    Dispatches a Celery task and returns the job ID immediately.
    """

    def execute(
        self, video_id: str, keypoints: List[Dict[str, Any]]
    ) -> CalibrationJobResult:
        """
        Start a calibration job.

        Args:
            video_id: ID of the video to calibrate.
            keypoints: List of keypoint dicts with pixel/pitch coordinates.

        Returns:
            CalibrationJobResult with the task ID.
        """
        # Dispatch Celery task
        task = calibrate_video_task.delay(video_id, keypoints)

        return CalibrationJobResult(
            job_id=task.id,
            status="PENDING",
            message=f"Calibration job started for video {video_id}",
        )
