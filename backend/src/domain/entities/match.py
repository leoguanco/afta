"""
Match Aggregate Root.

Represents a football match with its events.
This is a Domain object and MUST NOT import any external libraries.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from src.domain.entities.event import Event, EventType


@dataclass
class Match:
    """
    Aggregate Root representing a football match.

    Contains match metadata and a list of events.
    This is NOT frozen because we need to add events after creation.
    """

    match_id: str
    home_team_id: str
    away_team_id: str
    competition: Optional[str] = None
    season: Optional[str] = None
    match_date: Optional[str] = None
    events: List[Event] = field(default_factory=list)

    def add_event(self, event: Event) -> None:
        """Add an event to the match."""
        self.events.append(event)

    def get_events_by_type(self, event_type: EventType) -> List[Event]:
        """Filter events by type."""
        return [e for e in self.events if e.event_type == event_type]

    def get_events_by_player(self, player_id: str) -> List[Event]:
        """Filter events by player."""
        return [e for e in self.events if e.player_id == player_id]

    def __repr__(self) -> str:
        return f"Match({self.match_id}: {self.home_team_id} vs {self.away_team_id}, {len(self.events)} events)"
