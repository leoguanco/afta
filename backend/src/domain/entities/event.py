"""
Event Entity.

Represents a single match event (Pass, Shot, Carry, etc.).
This is a Domain object and MUST NOT import any external libraries.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from src.domain.value_objects.coordinates import Coordinates


class EventType(Enum):
    """Standardized event types across all data sources."""

    PASS = "pass"
    SHOT = "shot"
    CARRY = "carry"
    DRIBBLE = "dribble"
    TACKLE = "tackle"
    INTERCEPTION = "interception"
    CLEARANCE = "clearance"
    FOUL = "foul"
    GOAL = "goal"


@dataclass(frozen=True)
class Event:
    """
    Immutable Entity representing a match event.

    Attributes:
        event_id: Unique identifier for the event.
        event_type: Type of event (Pass, Shot, etc.).
        timestamp: Time in seconds from match start.
        coordinates: Location on the pitch (normalized to 105x68m).
        player_id: ID of the player who performed the event.
        end_coordinates: End location for events like passes (optional).
        team_id: ID of the team (optional).
    """

    event_id: str
    event_type: EventType
    timestamp: float
    coordinates: Coordinates
    player_id: str
    end_coordinates: Optional[Coordinates] = None
    team_id: Optional[str] = None

    def __repr__(self) -> str:
        return f"Event({self.event_type.value} at {self.timestamp:.1f}s by {self.player_id})"
