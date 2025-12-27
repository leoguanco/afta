"""
ObjectDetector Port (Interface).

Defines the contract for object detection implementations.
This is a Domain Port and MUST NOT import any external libraries.
"""

from abc import ABC, abstractmethod
from typing import List

from src.domain.value_objects.bounding_box import BoundingBox


class ObjectDetector(ABC):
    """
    Abstract interface for object detection.

    Concrete implementations (e.g., YOLODetector) will be in Infrastructure.
    """

    @abstractmethod
    def detect(self, frame) -> List[BoundingBox]:
        """
        Detect objects in a single frame.

        Args:
            frame: Image frame (numpy array in Infrastructure).

        Returns:
            List of detected bounding boxes.
        """
        ...

    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """
        Load the detection model.

        Args:
            model_path: Path to the model weights.
        """
        ...
