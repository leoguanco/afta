"""
ObjectTracker Port (Interface).

Defines the contract for object tracking implementations.
This is a Domain Port and MUST NOT import any external libraries.
"""

from abc import ABC, abstractmethod
from typing import List

from src.domain.value_objects.bounding_box import BoundingBox
from src.domain.value_objects.trajectory import Trajectory


class ObjectTracker(ABC):
    """
    Abstract interface for object tracking.

    Concrete implementations (e.g., ByteTracker) will be in Infrastructure.
    """

    @abstractmethod
    def update(self, detections: List[BoundingBox], frame_id: int) -> List[Trajectory]:
        """
        Update tracker with new detections and return trajectories.

        Args:
            detections: List of bounding boxes from the detector.
            frame_id: Current frame number.

        Returns:
            List of trajectories with assigned object IDs.
        """
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset the tracker state for a new video."""
        ...
