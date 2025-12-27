"""
KeypointDetector Port (Interface).

Defines the contract for detecting pitch landmarks in images.
This is a Domain Port and MUST NOT import any external libraries.
"""

from abc import ABC, abstractmethod
from typing import List

from src.domain.value_objects.keypoint import Keypoint


class KeypointDetector(ABC):
    """
    Abstract interface for pitch keypoint detection.

    Concrete implementations will use computer vision in Infrastructure.
    """

    @abstractmethod
    def detect(self, frame) -> List[Keypoint]:
        """
        Detect pitch landmarks in a frame.

        Args:
            frame: Image frame (numpy array in Infrastructure).

        Returns:
            List of detected keypoints with pixel and pitch coordinates.
        """
        ...
