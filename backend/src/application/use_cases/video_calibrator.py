"""
VideoCalibrator - Application Layer
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.domain.ports.calibration_port import CalibrationPort

@dataclass
class CalibrationJobResult:
    job_id: str
    status: str
    message: Optional[str] = None

class VideoCalibrator:
    def __init__(self, dispatcher: CalibrationPort):
        self.dispatcher = dispatcher
        
    def execute(self, video_id: str, keypoints: List[Dict[str, Any]]) -> CalibrationJobResult:
        job_id = self.dispatcher.start_calibration(video_id, keypoints)
        return CalibrationJobResult(
            job_id=job_id,
            status="PENDING",
            message=f"Calibration job started for video {video_id}"
        )
