"""
CalibrationPort - Domain Layer
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class CalibrationPort(ABC):
    @abstractmethod
    def start_calibration(self, video_id: str, keypoints: List[Dict[str, Any]]) -> str:
        """Dispatch calibration job. Returns job ID."""
        ...
