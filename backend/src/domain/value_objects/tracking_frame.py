"""
TrackingFrame Value Object - Domain Layer

Represents a single frame of tracking data with player positions.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass(frozen=True)
class PlayerPosition:
    """Position of a single player in a frame."""
    player_id: str
    x: float  # meters (0-105)
    y: float  # meters (0-68)
    team: str = "unknown"
    
    def distance_to(self, other: "PlayerPosition") -> float:
        """Calculate Euclidean distance to another position."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass(frozen=True)
class BallPosition:
    """Position of the ball in a frame."""
    x: float
    y: float
    z: Optional[float] = None  # Height if available


@dataclass
class TrackingFrame:
    """
    Value object representing tracking data for a single frame.
    
    Contains positions of all players and the ball at a specific moment.
    All coordinates are in metric pitch units (0-105m x 0-68m).
    """
    
    frame_id: int
    timestamp: float  # seconds from start
    home_players: List[PlayerPosition] = field(default_factory=list)
    away_players: List[PlayerPosition] = field(default_factory=list)
    ball: Optional[BallPosition] = None
    period: int = 1
    
    @property
    def all_players(self) -> List[PlayerPosition]:
        """Get all players from both teams."""
        return self.home_players + self.away_players
    
    def get_player(self, player_id: str) -> Optional[PlayerPosition]:
        """Find a specific player by ID."""
        for player in self.all_players:
            if player.player_id == player_id:
                return player
        return None
    
    def get_team_centroid(self, team: str) -> Tuple[float, float]:
        """Calculate the centroid of a team's positions."""
        players = self.home_players if team == "home" else self.away_players
        if not players:
            return (52.5, 34.0)  # Center of pitch
        
        avg_x = sum(p.x for p in players) / len(players)
        avg_y = sum(p.y for p in players) / len(players)
        return (avg_x, avg_y)
    
    def player_count(self) -> Dict[str, int]:
        """Count players per team."""
        return {
            "home": len(self.home_players),
            "away": len(self.away_players),
            "total": len(self.all_players)
        }
