"""
PhaseFeatures Value Object - Domain Layer

Feature vector extracted from tracking data for phase classification.
"""
from dataclasses import dataclass
from typing import Tuple
import numpy as np


@dataclass(frozen=True)
class PhaseFeatures:
    """
    Feature vector for phase classification.
    
    All features are extracted from a single frame of tracking data.
    Designed to capture the spatial organization and movement of both teams.
    """
    
    # Team centroid positions (meters on 105x68 pitch)
    home_centroid_x: float
    home_centroid_y: float
    away_centroid_x: float
    away_centroid_y: float
    
    # Team spread (standard deviation of positions)
    home_spread_x: float
    home_spread_y: float
    away_spread_x: float
    away_spread_y: float
    
    # Ball position
    ball_x: float
    ball_y: float
    
    # Ball velocity (meters per second)
    ball_velocity_x: float
    ball_velocity_y: float
    
    # Defensive line heights (average y of back 4)
    home_defensive_line: float
    away_defensive_line: float
    
    # Possession probability (0-1, based on proximity to ball)
    home_possession_prob: float
    
    def to_vector(self) -> np.ndarray:
        """Convert features to numpy array for ML model."""
        return np.array([
            self.home_centroid_x,
            self.home_centroid_y,
            self.away_centroid_x,
            self.away_centroid_y,
            self.home_spread_x,
            self.home_spread_y,
            self.away_spread_x,
            self.away_spread_y,
            self.ball_x,
            self.ball_y,
            self.ball_velocity_x,
            self.ball_velocity_y,
            self.home_defensive_line,
            self.away_defensive_line,
            self.home_possession_prob,
        ], dtype=np.float32)
    
    @classmethod
    def feature_names(cls) -> list[str]:
        """Return list of feature names for interpretability."""
        return [
            "home_centroid_x",
            "home_centroid_y",
            "away_centroid_x",
            "away_centroid_y",
            "home_spread_x",
            "home_spread_y",
            "away_spread_x",
            "away_spread_y",
            "ball_x",
            "ball_y",
            "ball_velocity_x",
            "ball_velocity_y",
            "home_defensive_line",
            "away_defensive_line",
            "home_possession_prob",
        ]
    
    @classmethod
    def num_features(cls) -> int:
        """Return number of features."""
        return 15
    
    @classmethod
    def from_tracking_frame(
        cls,
        home_positions: list[Tuple[float, float]],
        away_positions: list[Tuple[float, float]],
        ball_position: Tuple[float, float],
        ball_velocity: Tuple[float, float] = (0.0, 0.0),
    ) -> "PhaseFeatures":
        """
        Extract features from raw tracking data.
        
        Args:
            home_positions: List of (x, y) positions for home team
            away_positions: List of (x, y) positions for away team
            ball_position: (x, y) position of ball
            ball_velocity: (vx, vy) velocity of ball
        """
        # Calculate centroids
        home_x = [p[0] for p in home_positions] if home_positions else [52.5]
        home_y = [p[1] for p in home_positions] if home_positions else [34.0]
        away_x = [p[0] for p in away_positions] if away_positions else [52.5]
        away_y = [p[1] for p in away_positions] if away_positions else [34.0]
        
        home_centroid = (np.mean(home_x), np.mean(home_y))
        away_centroid = (np.mean(away_x), np.mean(away_y))
        
        # Calculate spreads
        home_spread = (np.std(home_x) if len(home_x) > 1 else 0.0,
                       np.std(home_y) if len(home_y) > 1 else 0.0)
        away_spread = (np.std(away_x) if len(away_x) > 1 else 0.0,
                       np.std(away_y) if len(away_y) > 1 else 0.0)
        
        # Calculate defensive lines (average of lowest 4 players)
        home_sorted_x = sorted(home_x)[:4] if len(home_x) >= 4 else home_x
        away_sorted_x = sorted(away_x, reverse=True)[:4] if len(away_x) >= 4 else away_x
        home_def_line = np.mean(home_sorted_x) if home_sorted_x else 15.0
        away_def_line = np.mean(away_sorted_x) if away_sorted_x else 90.0
        
        # Calculate possession probability
        home_ball_dist = min(
            np.sqrt((p[0] - ball_position[0])**2 + (p[1] - ball_position[1])**2)
            for p in home_positions
        ) if home_positions else 100.0
        away_ball_dist = min(
            np.sqrt((p[0] - ball_position[0])**2 + (p[1] - ball_position[1])**2)
            for p in away_positions
        ) if away_positions else 100.0
        
        # Sigmoid-based possession probability
        dist_diff = away_ball_dist - home_ball_dist
        home_poss_prob = 1.0 / (1.0 + np.exp(-dist_diff / 2.0))
        
        return cls(
            home_centroid_x=home_centroid[0],
            home_centroid_y=home_centroid[1],
            away_centroid_x=away_centroid[0],
            away_centroid_y=away_centroid[1],
            home_spread_x=home_spread[0],
            home_spread_y=home_spread[1],
            away_spread_x=away_spread[0],
            away_spread_y=away_spread[1],
            ball_x=ball_position[0],
            ball_y=ball_position[1],
            ball_velocity_x=ball_velocity[0],
            ball_velocity_y=ball_velocity[1],
            home_defensive_line=home_def_line,
            away_defensive_line=away_def_line,
            home_possession_prob=home_poss_prob,
        )
