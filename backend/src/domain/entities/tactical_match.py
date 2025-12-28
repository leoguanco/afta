"""
TacticalMatch Entity - Domain Layer

Rich entity representing a match with tactical event data and metrics.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class EventType(Enum):
    """Event types for tactical analysis."""
    PASS = "pass"
    SHOT = "shot"
    CARRY = "carry"
    DRIBBLE = "dribble"
    DEFENSIVE_ACTION = "defensive_action"
    PRESSURE = "pressure"
    TACKLE = "tackle"
    INTERCEPTION = "interception"


@dataclass
class MatchEvent:
    """Value object for match event."""
    event_id: str
    event_type: EventType
    team: str  # Renamed from team_id for consistency
    player_id: str
    minute: int = 0
    timestamp: float = 0.0
    x: float = 0.0  # Kept for backwards compatibility
    y: float = 0.0
    start_x: float = 0.0  # Start position for passes/carries
    start_y: float = 0.0
    end_x: float = 0.0    # End position for passes/carries
    end_y: float = 0.0
    
    def __post_init__(self):
        # If start/end not set, use x/y
        if self.start_x == 0.0 and self.x != 0.0:
            self.start_x = self.x
            self.start_y = self.y


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


@dataclass
class XTEvent:
    """Value object for xT-annotated event."""
    event_id: str
    event_type: EventType
    player_id: str
    start_xt: float
    end_xt: float
    xt_change: float


@dataclass
class XTChainResult:
    """Value object for xT possession chain result."""
    events: List[XTEvent]
    total_xt: float
    average_xt_per_action: float


class TacticalMatch:
    """
    Rich domain entity for tactical match analysis.
    
    Encapsulates match events and provides methods to calculate
    tactical metrics like PPDA, pressing intensity, and Expected Threat.
    """
    
    def __init__(
        self,
        match_id: str,
        events: List[MatchEvent],
        home_team: str = "home",
        away_team: str = "away",
        pitch_length: float = 105.0
    ):
        """
        Initialize tactical match.
        
        Args:
            match_id: Match identifier
            events: List of match events
            home_team: Home team identifier
            away_team: Away team identifier
            pitch_length: Pitch length for zone calculations
        """
        self.match_id = match_id
        self.events = events
        self.home_team = home_team
        self.away_team = away_team
        self.pitch_length = pitch_length
        self.third_length = pitch_length / 3.0
        
        # Lazy-loaded xT grid
        self._xt_grid = None
    
    @property
    def xt_grid(self):
        """Get xT grid (lazy loaded)."""
        if self._xt_grid is None:
            from src.domain.value_objects.expected_threat_grid import ExpectedThreatGrid
            self._xt_grid = ExpectedThreatGrid()
        return self._xt_grid
    
    def calculate_xt_chain(self, team: str) -> XTChainResult:
        """
        Calculate Expected Threat (xT) for a team's possession actions.
        
        xT measures the probability of scoring from each location.
        This method calculates xT gained/lost for each action.
        
        Args:
            team: Team to calculate xT for
            
        Returns:
            XTChainResult with annotated events and totals
        """
        progressive_events = {EventType.PASS, EventType.CARRY, EventType.DRIBBLE, EventType.SHOT}
        
        xt_events = []
        total_xt = 0.0
        
        for event in self.events:
            if event.team != team or event.event_type not in progressive_events:
                continue
            
            # Get xT values at start and end positions
            start_xt = self.xt_grid.get_threat_at_pitch_location(
                event.start_x, event.start_y
            )
            end_xt = self.xt_grid.get_threat_at_pitch_location(
                event.end_x, event.end_y
            )
            xt_change = end_xt - start_xt
            
            xt_events.append(XTEvent(
                event_id=event.event_id,
                event_type=event.event_type,
                player_id=event.player_id,
                start_xt=start_xt,
                end_xt=end_xt,
                xt_change=xt_change
            ))
            
            total_xt += xt_change
        
        avg_xt = total_xt / len(xt_events) if xt_events else 0.0
        
        return XTChainResult(
            events=xt_events,
            total_xt=total_xt,
            average_xt_per_action=avg_xt
        )
    
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
            if (e.team == attacking_team and
                e.event_type == EventType.PASS and
                self._in_attacking_two_thirds(e.x or e.start_x, attacking_team))
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
            if (e.team == defending_team and
                e.event_type in defensive_event_types)
        )
        
        ppda = float('inf') if defensive_actions == 0 else passes_allowed / defensive_actions
        
        return PPDAResult(
            passes_allowed=passes_allowed,
            defensive_actions=defensive_actions,
            ppda=ppda
        )
    
    def calculate_pressing_metrics(self, team: str) -> PressureMetrics:
        """
        Calculate pressing intensity by pitch zone.
        
        Args:
            team: Team to calculate metrics for
            
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
            if event.team != team or event.event_type not in pressure_types:
                continue
            
            zone = self._get_zone(event.x or event.start_x)
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
    
    def get_events_by_team(self, team: str) -> List[MatchEvent]:
        """Filter events by team."""
        return [e for e in self.events if e.team == team]
    
    def _in_attacking_two_thirds(self, x: float, team: str) -> bool:
        """Check if position is in attacking 2/3 of pitch."""
        if team == self.home_team:
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

