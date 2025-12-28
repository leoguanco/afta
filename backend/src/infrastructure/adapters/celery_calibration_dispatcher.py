"""
CeleryCalibrationDispatcher - Infrastructure Adapter
"""
from typing import List, Dict, Any
from src.domain.ports.calibration_port import CalibrationPort
from src.infrastructure.worker.celery_app import celery_app

class CeleryCalibrationDispatcher(CalibrationPort):
    def start_calibration(self, video_id: str, keypoints: List[Dict[str, Any]]) -> str:
        task = celery_app.send_task(
            'src.infrastructure.worker.tasks.calibration_tasks.calibrate_video_task',
            args=[video_id, keypoints]
        )
        return task.id
