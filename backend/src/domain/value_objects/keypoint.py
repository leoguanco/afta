"""
Keypoint Value Object.

Represents a correspondence between pixel coordinates and pitch coordinates.
This is a Domain object and MUST NOT import any external libraries.
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Keypoint:
    """
    Immutable Value Object representing a landmark correspondence.

    Maps a point in video pixel space to a point in pitch metric space.

    Attributes:
        pixel_x: X coordinate in pixel space.
        pixel_y: Y coordinate in pixel space.
        pitch_x: X coordinate on pitch (0-105 meters).
        pitch_y: Y coordinate on pitch (0-68 meters).
        name: Optional landmark name (e.g., "corner_left_top", "center_spot").
    """

    pixel_x: float
    pixel_y: float
    pitch_x: float
    pitch_y: float
    name: Optional[str] = None

    @property
    def pixel_coords(self) -> Tuple[float, float]:
        """Return pixel coordinates as tuple."""
        return (self.pixel_x, self.pixel_y)

    @property
    def pitch_coords(self) -> Tuple[float, float]:
        """Return pitch coordinates as tuple."""
        return (self.pitch_x, self.pitch_y)

    def __repr__(self) -> str:
        return f"Keypoint(pixel=({self.pixel_x:.0f},{self.pixel_y:.0f}) -> pitch=({self.pitch_x:.1f}m,{self.pitch_y:.1f}m))"
