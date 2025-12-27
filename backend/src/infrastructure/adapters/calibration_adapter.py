from typing import List, Dict, Any
from src.domain.ports.calibration_job_dispatcher import CalibrationJobDispatcher
from src.infrastructure.worker.tasks.calibration_tasks import calibrate_video_task

class CeleryCalibrationJobDispatcher(CalibrationJobDispatcher):
    """
    Celery implementation of the CalibrationJobDispatcher port.
    """
    
    def dispatch(self, video_id: str, keypoints: List[Dict[str, Any]]) -> str:
        """
        Dispatch the calibration task to Celery.
        """
        task = calibrate_video_task.delay(video_id, keypoints)
        return task.id
