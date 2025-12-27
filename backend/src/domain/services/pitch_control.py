"""
Pitch Control Service - Domain Layer

Implements Spearman 2018 pitch control model for calculating spatial control probability.
Uses numpy for vectorized grid calculations.
"""
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


@dataclass
class PlayerPosition:
    """Player position and velocity at a given frame."""
    player_id: str
    team_id: str
    x: float  # meters
    y: float  # meters
    vx: float = 0.0  # velocity x (m/s)
    vy: float = 0.0  # velocity y (m/s)


@dataclass
class PitchControlGrid:
    """Pitch control probability grid."""
    home_control: np.ndarray  # Shape: (grid_height, grid_width)
    away_control: np.ndarray  # Shape: (grid_height, grid_width)
    grid_width: int
    grid_height: int
    pitch_length: float  # meters
    pitch_width: float  # meters


class PitchControlService:
    """
    Domain service for calculating pitch control using Spearman 2018 model (simplified).
    Pure domain logic using numpy vectorization.
    """
    
    def __init__(
        self,
        pitch_length: float = 105.0,
        pitch_width: float = 68.0,
        grid_width: int = 32,
        grid_height: int = 24,
        reaction_time: float = 0.7,
        max_speed: float = 5.0
    ):
        """
        Initialize pitch control service.
        
        Args:
            pitch_length: Length of pitch (meters)
            pitch_width: Width of pitch (meters)
            grid_width: Number of grid cells horizontally
            grid_height: Number of grid cells vertically
            reaction_time: Player reaction time (seconds)
            max_speed: Maximum player speed (m/s)
        """
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.reaction_time = reaction_time
        self.max_speed = max_speed
    
    def calculate_pitch_control(
        self,
        players: List[PlayerPosition],
        ball_x: float,
        ball_y: float
    ) -> PitchControlGrid:
        """
        Calculate pitch control grid for the current frame.
        
        Args:
            players: List of player positions
            ball_x: Ball x position (meters)
            ball_y: Ball y position (meters)
            
        Returns:
            PitchControlGrid with home and away team control probabilities
        """
        # Create grid coordinates
        x_grid, y_grid = self._create_grid()
        
        # Separate teams
        home_players = [p for p in players if p.team_id == "home"]
        away_players = [p for p in players if p.team_id == "away"]
        
        # Calculate control for each team
        home_control = self._calculate_team_control(home_players, x_grid, y_grid)
        away_control = self._calculate_team_control(away_players, x_grid, y_grid)
        
        # Normalize so home_control + away_control = 1
        total_control = home_control + away_control + 1e-10  # avoid division by zero
        home_control = home_control / total_control
        away_control = away_control / total_control
        
        return PitchControlGrid(
            home_control=home_control,
            away_control=away_control,
            grid_width=self.grid_width,
            grid_height=self.grid_height,
            pitch_length=self.pitch_length,
            pitch_width=self.pitch_width
        )
    
    def _create_grid(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create grid coordinates.
        
        Returns:
            Tuple of (x_grid, y_grid) with shape (grid_height, grid_width)
        """
        x = np.linspace(0, self.pitch_length, self.grid_width)
        y = np.linspace(0, self.pitch_width, self.grid_height)
        x_grid, y_grid = np.meshgrid(x, y)
        
        return x_grid, y_grid
    
    def _calculate_team_control(
        self,
        players: List[PlayerPosition],
        x_grid: np.ndarray,
        y_grid: np.ndarray
    ) -> np.ndarray:
        """
        Calculate team control using simplified Spearman model.
        
        Args:
            players: List of players from one team
            x_grid: Grid x coordinates
            y_grid: Grid y coordinates
            
        Returns:
            Control probability grid
        """
        if not players:
            return np.zeros_like(x_grid)
        
        # Initialize team control
        team_control = np.zeros_like(x_grid)
        
        # For each player, calculate their influence
        for player in players:
            player_influence = self._calculate_player_influence(
                player, x_grid, y_grid
            )
            # Combine using max (dominant player at each location)
            team_control = np.maximum(team_control, player_influence)
        
        return team_control
    
    def _calculate_player_influence(
        self,
        player: PlayerPosition,
        x_grid: np.ndarray,
        y_grid: np.ndarray
    ) -> np.ndarray:
        """
        Calculate a single player's influence using time-to-intercept.
        
        Args:
            player: Player position
            x_grid: Grid x coordinates
            y_grid: Grid y coordinates
            
        Returns:
            Influence grid for this player
        """
        # Distance from player to each grid point
        dx = x_grid - player.x
        dy = y_grid - player.y
        distance = np.sqrt(dx**2 + dy**2)
        
        # Time to reach each grid point
        time_to_reach = self.reaction_time + distance / self.max_speed
        
        # Convert to influence (inverse exponential decay)
        # Lower time = higher influence
        influence = np.exp(-time_to_reach / 2.0)
        
        return influence
