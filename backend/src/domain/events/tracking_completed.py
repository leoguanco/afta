"""
Tracking Completed Event.

Emitted when video tracking (YOLO + ByteTrack) completes successfully.
Triggers downstream processes like metrics calculation.
"""
from dataclasses import dataclass
from typing import Optional

from .base import DomainEvent


@dataclass(frozen=True)
class TrackingCompletedEvent(DomainEvent):
    """
    Event indicating that video tracking has completed.
    
    This event triggers:
    - Automatic metrics calculation
    - UI notification for user
    - Potential analytics/logging
    
    Attributes:
        match_id: ID of the match that was tracked
        video_path: Path to the processed video
        trajectory_path: Path to the saved trajectory parquet
        frames_processed: Number of frames analyzed
        players_detected: Number of unique players detected
    """
    match_id: str = ""
    video_path: str = ""
    trajectory_path: str = ""
    frames_processed: int = 0
    players_detected: int = 0
    
    def _event_data(self) -> dict:
        return {
            "match_id": self.match_id,
            "video_path": self.video_path,
            "trajectory_path": self.trajectory_path,
            "frames_processed": self.frames_processed,
            "players_detected": self.players_detected,
        }
