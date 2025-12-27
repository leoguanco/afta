"""
Tactical Events Service - Domain Layer

Calculates tactical metrics from event streams (PPDA, pressing intensity).
"""
from dataclasses import dataclass
from typing import List
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
    """Single match event."""
    event_id: str
    event_type: EventType
    team_id: str
    player_id: str
    timestamp: float
    x: float
    y: float


@dataclass
class PPDAResult:
    """PPDA (Passes Per Defensive Action) result."""
    team_id: str
    passes_allowed: int
    defensive_actions: int
    ppda: float  # passes_allowed / defensive_actions


@dataclass
class PressureMetrics:
    """Pressing metrics by pitch zone."""
    team_id: str
    defensive_third_presses: int
    middle_third_presses: int
    attacking_third_presses: int
    total_presses: int


class TacticalEventsService:
    """
    Domain service for calculating tactical metrics from event data.
    Pure domain logic without external dependencies.
    """
    
    def __init__(self, pitch_length: float = 105.0):
        """
        Initialize tactical events service.
        
        Args:
            pitch_length: Length of pitch for zone calculations (meters)
        """
        self.pitch_length = pitch_length
        self.third_length = pitch_length / 3.0
    
    def calculate_ppda(
        self,
        events: List[MatchEvent],
        defending_team: str,
        attacking_team: str
    ) -> PPDAResult:
        """
        Calculate PPDA for the defending team.
        
        PPDA = Number of opposition passes / Number of defensive actions
        Lower PPDA indicates more intense pressing.
        
        Args:
            events: List of match events
            defending_team: ID of defending team
            attacking_team: ID of attacking team
            
        Returns:
            PPDAResult with calculated PPDA
        """
        # Count opposition passes (in defensive 2/3 of pitch)
        passes_allowed = 0
        for event in events:
            if (event.team_id == attacking_team and 
                event.event_type == EventType.PASS and
                self._in_attacking_two_thirds(event.x, attacking_team)):
                passes_allowed += 1
        
        # Count defensive actions
        defensive_actions = 0
        defensive_event_types = {
            EventType.DEFENSIVE_ACTION,
            EventType.TACKLE,
            EventType.INTERCEPTION,
            EventType.PRESSURE
        }
        
        for event in events:
            if (event.team_id == defending_team and 
                event.event_type in defensive_event_types):
                defensive_actions += 1
        
        # Calculate PPDA
        if defensive_actions == 0:
            ppda = float('inf')
        else:
            ppda = passes_allowed / defensive_actions
        
        return PPDAResult(
            team_id=defending_team,
            passes_allowed=passes_allowed,
            defensive_actions=defensive_actions,
            ppda=ppda
        )
    
    def calculate_pressure_metrics(
        self,
        events: List[MatchEvent],
        team_id: str
    ) -> PressureMetrics:
        """
        Calculate pressing intensity by pitch zone.
        
        Args:
            events: List of match events
            team_id: Team to calculate metrics for
            
        Returns:
            PressureMetrics with zone breakdowns
        """
        defensive_third = 0
        middle_third = 0
        attacking_third = 0
        
        pressure_types = {
            EventType.PRESSURE,
            EventType.DEFENSIVE_ACTION,
            EventType.TACKLE
        }
        
        for event in events:
            if event.team_id != team_id:
                continue
            
            if event.event_type not in pressure_types:
                continue
            
            # Determine zone
            zone = self._get_zone(event.x)
            if zone == "defensive":
                defensive_third += 1
            elif zone == "middle":
                middle_third += 1
            elif zone == "attacking":
                attacking_third += 1
        
        total = defensive_third + middle_third + attacking_third
        
        return PressureMetrics(
            team_id=team_id,
            defensive_third_presses=defensive_third,
            middle_third_presses=middle_third,
            attacking_third_presses=attacking_third,
            total_presses=total
        )
    
    def _in_attacking_two_thirds(self, x: float, team_id: str) -> bool:
        """
        Check if position is in attacking 2/3 of pitch.
        
        Args:
            x: X coordinate
            team_id: Team ID (to determine direction)
            
        Returns:
            True if in attacking 2/3
        """
        # Assume home attacks right (x > third_length)
        # away attacks left (x < 2*third_length)
        if team_id == "home":
            return x > self.third_length
        else:
            return x < (2 * self.third_length)
    
    def _get_zone(self, x: float) -> str:
        """
        Get pitch zone (defensive/middle/attacking third).
        
        Args:
            x: X coordinate
            
        Returns:
            Zone name
        """
        if x < self.third_length:
            return "defensive"
        elif x < (2 * self.third_length):
            return "middle"
        else:
            return "attacking"
