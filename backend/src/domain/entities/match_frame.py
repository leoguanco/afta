"""
MatchFrame Entity - Domain Layer

Rich entity representing the game state at a single moment in time.
"""
from dataclasses import dataclass
from typing import List, Dict
import numpy as np


@dataclass
class PlayerPosition:
    """Value object for player position."""
    player_id: str
    team_id: str
    x: float  # meters
    y: float  # meters
    vx: float = 0.0  # velocity x (m/s)
    vy: float = 0.0  # velocity y (m/s)


@dataclass
class BallPosition:
    """Value object for ball position."""
    x: float
    y: float


@dataclass
class PitchControlGrid:
    """Value object for pitch control result."""
    home_control: np.ndarray
    away_control: np.ndarray
    grid_width: int
    grid_height: int


class MatchFrame:
    """
    Rich domain entity representing the game state at one moment.
    
    Encapsulates all player and ball positions for a frame and provides
    methods to calculate spatial metrics like pitch control.
    """
    
    def __init__(
        self,
        frame_id: int,
        players: List[PlayerPosition],
        ball: BallPosition,
        pitch_length: float = 105.0,
        pitch_width: float = 68.0,
        grid_width: int = 32,
        grid_height: int = 24
    ):
        """
        Initialize match frame.
        
        Args:
            frame_id: Frame identifier
            players: List of player positions
            ball: Ball position
            pitch_length: Pitch length (meters)
            pitch_width: Pitch width (meters)
            grid_width: Grid resolution (width)
            grid_height: Grid resolution (height)
        """
        self.frame_id = frame_id
        self.players = players
        self.ball = ball
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        self.grid_width = grid_width
        self.grid_height = grid_height
        
        # Cache
        self._pitch_control: PitchControlGrid | None = None
    
    def calculate_pitch_control(
        self,
        reaction_time: float = 0.7,
        max_speed: float = 5.0
    ) -> PitchControlGrid:
        """
        Calculate pitch control grid using Spearman 2018 model.
        
        Args:
            reaction_time: Player reaction time (seconds)
            max_speed: Maximum player speed (m/s)
            
        Returns:
            PitchControlGrid with team control probabilities
        """
        if self._pitch_control is not None:
            return self._pitch_control
        
        # Create grid
        x_grid, y_grid = self._create_grid()
        
        # Separate teams
        home_players = [p for p in self.players if p.team_id == "home"]
        away_players = [p for p in self.players if p.team_id == "away"]
        
        # Calculate control for each team
        home_control = self._calculate_team_control(
            home_players, x_grid, y_grid, reaction_time, max_speed
        )
        away_control = self._calculate_team_control(
            away_players, x_grid, y_grid, reaction_time, max_speed
        )
        
        # Normalize
        total = home_control + away_control + 1e-10
        home_control = home_control / total
        away_control = away_control / total
        
        self._pitch_control = PitchControlGrid(
            home_control=home_control,
            away_control=away_control,
            grid_width=self.grid_width,
            grid_height=self.grid_height
        )
        
        return self._pitch_control
    
    def get_team_dominance(self) -> Dict[str, float]:
        """
        Get overall team dominance scores.
        
        Returns:
            Dictionary with "home" and "away" dominance (0-1)
        """
        control = self.calculate_pitch_control()
        
        return {
            "home": float(np.mean(control.home_control)),
            "away": float(np.mean(control.away_control))
        }
    
    def _create_grid(self) -> tuple[np.ndarray, np.ndarray]:
        """Create spatial grid coordinates."""
        x = np.linspace(0, self.pitch_length, self.grid_width)
        y = np.linspace(0, self.pitch_width, self.grid_height)
        return np.meshgrid(x, y)
    
    def _calculate_team_control(
        self,
        players: List[PlayerPosition],
        x_grid: np.ndarray,
        y_grid: np.ndarray,
        reaction_time: float,
        max_speed: float
    ) -> np.ndarray:
        """Calculate team control grid."""
        if not players:
            return np.zeros_like(x_grid)
        
        team_control = np.zeros_like(x_grid)
        
        for player in players:
            influence = self._calculate_player_influence(
                player, x_grid, y_grid, reaction_time, max_speed
            )
            team_control = np.maximum(team_control, influence)
        
        return team_control
    
    def _calculate_player_influence(
        self,
        player: PlayerPosition,
        x_grid: np.ndarray,
        y_grid: np.ndarray,
        reaction_time: float,
        max_speed: float
    ) -> np.ndarray:
        """Calculate single player's influence."""
        dx = x_grid - player.x
        dy = y_grid - player.y
        distance = np.sqrt(dx**2 + dy**2)
        
        time_to_reach = reaction_time + distance / max_speed
        influence = np.exp(-time_to_reach / 2.0)
        
        return influence
    
    def __repr__(self) -> str:
        return f"MatchFrame(frame_id={self.frame_id}, players={len(self.players)})"
