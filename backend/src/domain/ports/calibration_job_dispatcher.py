from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class CalibrationJobDispatcher(ABC):
    """
    Port for dispatching calibration jobs to background workers.
    """
    
    @abstractmethod
    def dispatch(self, video_id: str, keypoints: List[Dict[str, Any]]) -> str:
        """
        Dispatch a calibration job.
        
        Args:
            video_id: ID of the video to calibrate
            keypoints: User-provided keypoints
            
        Returns:
            Job ID (task ID)
        """
        pass
