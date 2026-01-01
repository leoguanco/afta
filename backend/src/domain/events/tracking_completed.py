"""
Tracking Completed Event - Domain Layer

Event emitted when video tracking processing is finished.
"""
from dataclasses import dataclass
import uuid
from datetime import datetime

@dataclass
class TrackingCompletedEvent:
    aggregate_id: str
    match_id: str
    video_path: str
    trajectory_path: str
    frames_processed: int
    players_detected: int
    event_id: str = None
    timestamp: datetime = None

    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now()
