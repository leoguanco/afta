"""Domain Events Package."""
from .base import DomainEvent
from .video_processed import TrackingCompletedEvent
from .calibration_completed import CalibrationCompletedEvent

__all__ = [
    "DomainEvent",
    "TrackingCompletedEvent",
    "CalibrationCompletedEvent",
]

