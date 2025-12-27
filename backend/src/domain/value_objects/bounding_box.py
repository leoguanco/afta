"""
BoundingBox Value Object.

Represents a detection bounding box from the vision model.
This is a Domain object and MUST NOT import any external libraries.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class BoundingBox:
    """
    Immutable Value Object representing a detection bounding box.

    Coordinates are in pixel space (before homography transformation).

    Attributes:
        x1: Left edge X coordinate.
        y1: Top edge Y coordinate.
        x2: Right edge X coordinate.
        y2: Bottom edge Y coordinate.
        confidence: Detection confidence score (0-1).
        class_id: Class index from the model (0=player, 1=ball, etc.).
    """

    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int

    @property
    def center(self) -> Tuple[float, float]:
        """Calculate the center point of the bounding box."""
        cx = (self.x1 + self.x2) / 2
        cy = (self.y1 + self.y2) / 2
        return (cx, cy)

    @property
    def width(self) -> float:
        """Calculate the width of the bounding box."""
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        """Calculate the height of the bounding box."""
        return self.y2 - self.y1

    def __repr__(self) -> str:
        return f"BoundingBox(({self.x1:.0f},{self.y1:.0f})->({self.x2:.0f},{self.y2:.0f}), conf={self.confidence:.2f})"
