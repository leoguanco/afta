from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.domain.ports.calibration_job_dispatcher import CalibrationJobDispatcher


@dataclass
class CalibrationJobResult:
    """Result of starting a calibration job."""

    job_id: str
    status: str
    message: Optional[str] = None


class StartCalibrationUseCase:
    """
    Use Case to start an async calibration job.

    Dispatches a Celery task via the JobDispatcher port.
    """
    
    def __init__(self, job_dispatcher: CalibrationJobDispatcher):
        """
        Initialize the use case.
        
        Args:
            job_dispatcher: Port for dispatching background jobs.
        """
        self.job_dispatcher = job_dispatcher

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
        # Dispatch via Port
        job_id = self.job_dispatcher.dispatch(video_id, keypoints)

        return CalibrationJobResult(
            job_id=job_id,
            status="PENDING",
            message=f"Calibration job started for video {video_id}",
        )
