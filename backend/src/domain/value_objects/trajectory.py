"""
Trajectory Value Object.

Represents a single tracked object position at a specific frame.
This is a Domain object and MUST NOT import any external libraries.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ObjectType(Enum):
    """Types of trackable objects."""

    PLAYER = "player"
    BALL = "ball"
    REFEREE = "referee"
    GOALKEEPER = "goalkeeper"


@dataclass(frozen=True)
class Trajectory:
    """
    Immutable Value Object representing a tracked object position.

    Attributes:
        frame_id: Frame number in the video.
        object_id: Unique ID for the tracked object (persists across frames).
        x: X coordinate on the pitch (0-105 meters).
        y: Y coordinate on the pitch (0-68 meters).
        object_type: Type of object (player, ball, referee).
        confidence: Detection confidence score (0-1).
        team_id: Optional team identifier.
    """

    frame_id: int
    object_id: int
    x: float
    y: float
    object_type: ObjectType
    confidence: Optional[float] = None
    team_id: Optional[str] = None

    def __repr__(self) -> str:
        return f"Trajectory(frame={self.frame_id}, id={self.object_id}, pos=({self.x:.1f}, {self.y:.1f}))"
