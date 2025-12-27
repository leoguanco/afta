"""
Metrics Repository Port - Domain Layer

Interface for persisting tactical metrics (Ports & Adapters pattern).
"""
from abc import ABC, abstractmethod
from typing import List
import numpy as np


class MetricsRepository(ABC):
    """
    Port (interface) for metrics persistence.
    
    Infrastructure layer will provide concrete implementation.
    """
    
    @abstractmethod
    def save_pitch_control_frame(
        self,
        match_id: str,
        frame_id: int,
        home_control: np.ndarray,
        away_control: np.ndarray
    ) -> None:
        """Save pitch control grid for a frame."""
        pass
    
    @abstractmethod
    def save_physical_stats(
        self,
        match_id: str,
        player_id: str,
        total_distance: float,
        max_speed: float,
        sprint_count: int,
        avg_speed: float
    ) -> None:
        """Save physical statistics for a player."""
        pass
    
    @abstractmethod
    def save_ppda(
        self,
        match_id: str,
        team_id: str,
        passes_allowed: int,
        defensive_actions: int,
        ppda: float
    ) -> None:
        """Save PPDA metrics for a team."""
        pass
