"""
Calibration Completed Event.

Emitted when pitch calibration (homography computation) completes.
"""
from dataclasses import dataclass
from typing import List

from .base import DomainEvent


@dataclass(frozen=True)
class CalibrationCompletedEvent(DomainEvent):
    """
    Event indicating that pitch calibration has completed.
    
    This event enables:
    - Coordinate transformation from pixel to pitch coordinates
    - Accurate player position tracking
    
    Attributes:
        video_id: ID of the video that was calibrated
        keypoints_used: Number of keypoints used for calibration
        reprojection_error: Quality metric (lower is better)
    """
    video_id: str = ""
    keypoints_used: int = 0
    reprojection_error: float = 0.0
    
    def _event_data(self) -> dict:
        return {
            "video_id": self.video_id,
            "keypoints_used": self.keypoints_used,
            "reprojection_error": self.reprojection_error,
        }
