"""
Coordinates Value Object.

Represents a normalized pitch coordinate in meters (105x68 standard pitch).
This is a Domain object and MUST NOT import any external libraries.
"""

from dataclasses import dataclass


# Standard pitch dimensions in meters
PITCH_LENGTH_M = 105.0
PITCH_WIDTH_M = 68.0

# StatsBomb coordinate system
STATSBOMB_LENGTH = 120.0
STATSBOMB_WIDTH = 80.0


@dataclass(frozen=True)
class Coordinates:
    """
    Immutable Value Object representing a point on the pitch.

    All coordinates are normalized to the metric pitch (105m x 68m).
    """

    x: float  # 0 to 105 meters (length)
    y: float  # 0 to 68 meters (width)

    @classmethod
    def from_statsbomb(cls, x: float, y: float) -> "Coordinates":
        """
        Convert StatsBomb coordinates (0-120, 0-80) to Metric (0-105, 0-68).

        Linear scaling: metric = (statsbomb / max_statsbomb) * max_metric
        """
        metric_x = (x / STATSBOMB_LENGTH) * PITCH_LENGTH_M
        metric_y = (y / STATSBOMB_WIDTH) * PITCH_WIDTH_M
        return cls(x=metric_x, y=metric_y)

    @classmethod
    def from_metrica(cls, x: float, y: float) -> "Coordinates":
        """
        Convert Metrica coordinates (0-1, 0-1) to Metric (0-105, 0-68).

        Linear scaling: metric = normalized * max_metric
        """
        metric_x = x * PITCH_LENGTH_M
        metric_y = y * PITCH_WIDTH_M
        return cls(x=metric_x, y=metric_y)

    def __repr__(self) -> str:
        return f"Coordinates(x={self.x:.2f}m, y={self.y:.2f}m)"
