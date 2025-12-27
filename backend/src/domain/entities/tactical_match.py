"""
TacticalMatch Entity - Domain Layer

Rich entity representing a match with tactical event data and metrics.
"""
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum


class EventType(Enum):
    """Event types for tactical analysis."""
    PASS = "pass"
    DEFENSIVE_ACTION = "defensive_action"
    PRESSURE = "pressure"
    TACKLE = "tackle"
    INTERCEPTION = "interception"


@dataclass
class MatchEvent:
    """Value object for match event."""
    event_id: str
    event_type: EventType
    team_id: str
    player_id: str
    timestamp: float
    x: float
    y: float


@dataclass
class PPDAResult:
    """Value object for PPDA result."""
    passes_allowed: int
    defensive_actions: int
    ppda: float


@dataclass
class PressureMetrics:
    """Value object for pressure metrics."""
    defensive_third_presses: int
    middle_third_presses: int
    attacking_third_presses: int
    total_presses: int


class TacticalMatch:
    """
    Rich domain entity for tactical match analysis.
    
    Encapsulates match events and provides methods to calculate
    tactical metrics like PPDA and pressing intensity.
    """
    
    def __init__(
        self,
        match_id: str,
        events: List[MatchEvent],
        pitch_length: float = 105.0
    ):
        """
        Initialize tactical match.
        
        Args:
            match_id: Match identifier
            events: List of match events
            pitch_length: Pitch length for zone calculations
        """
        self.match_id = match_id
        self.events = events
        self.pitch_length = pitch_length
        self.third_length = pitch_length / 3.0
    
    def calculate_ppda(self, defending_team: str, attacking_team: str) -> PPDAResult:
        """
        Calculate PPDA (Passes Per Defensive Action).
        
        Lower PPDA indicates more intense pressing.
        
        Args:
            defending_team: ID of defending team
            attacking_team: ID of attacking team
            
        Returns:
            PPDAResult with PPDA metric
        """
        # Count opposition passes in attacking 2/3
        passes_allowed = sum(
            1 for e in self.events
            if (e.team_id == attacking_team and
                e.event_type == EventType.PASS and
                self._in_attacking_two_thirds(e.x, attacking_team))
        )
        
        # Count defensive actions
        defensive_event_types = {
            EventType.DEFENSIVE_ACTION,
            EventType.TACKLE,
            EventType.INTERCEPTION,
            EventType.PRESSURE
        }
        
        defensive_actions = sum(
            1 for e in self.events
            if (e.team_id == defending_team and
                e.event_type in defensive_event_types)
        )
        
        ppda = float('inf') if defensive_actions == 0 else passes_allowed / defensive_actions
        
        return PPDAResult(
            passes_allowed=passes_allowed,
            defensive_actions=defensive_actions,
            ppda=ppda
        )
    
    def calculate_pressing_metrics(self, team_id: str) -> PressureMetrics:
        """
        Calculate pressing intensity by pitch zone.
        
        Args:
            team_id: Team to calculate metrics for
            
        Returns:
            PressureMetrics with zone breakdown
        """
        pressure_types = {
            EventType.PRESSURE,
            EventType.DEFENSIVE_ACTION,
            EventType.TACKLE
        }
        
        defensive_third = 0
        middle_third = 0
        attacking_third = 0
        
        for event in self.events:
            if event.team_id != team_id or event.event_type not in pressure_types:
                continue
            
            zone = self._get_zone(event.x)
            if zone == "defensive":
                defensive_third += 1
            elif zone == "middle":
                middle_third += 1
            elif zone == "attacking":
                attacking_third += 1
        
        return PressureMetrics(
            defensive_third_presses=defensive_third,
            middle_third_presses=middle_third,
            attacking_third_presses=attacking_third,
            total_presses=defensive_third + middle_third + attacking_third
        )
    
    def get_events_by_type(self, event_type: EventType) -> List[MatchEvent]:
        """Filter events by type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def get_events_by_team(self, team_id: str) -> List[MatchEvent]:
        """Filter events by team."""
        return [e for e in self.events if e.team_id == team_id]
    
    def _in_attacking_two_thirds(self, x: float, team_id: str) -> bool:
        """Check if position is in attacking 2/3 of pitch."""
        if team_id == "home":
            return x > self.third_length
        else:
            return x < (2 * self.third_length)
    
    def _get_zone(self, x: float) -> str:
        """Get pitch zone (defensive/middle/attacking third)."""
        if x < self.third_length:
            return "defensive"
        elif x < (2 * self.third_length):
            return "middle"
        else:
            return "attacking"
    
    def __repr__(self) -> str:
        return f"TacticalMatch(match_id={self.match_id}, events={len(self.events)})"
