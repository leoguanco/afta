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

    # --- Read Methods ---
    
    @abstractmethod
    def get_physical_stats(self, match_id: str, team_id: str = None) -> List[dict]:
        """
        Get physical statistics for a match.
        
        Args:
            match_id: Match identifier
            team_id: Optional filter by team
            
        Returns:
            List of player stats dictionaries
        """
        pass
    
    @abstractmethod
    def get_ppda(self, match_id: str, team_id: str) -> dict:
        """
        Get PPDA metrics for a team.
        
        Args:
            match_id: Match identifier
            team_id: Team identifier
            
        Returns:
            PPDA stats dictionary
        """
        pass
    
    @abstractmethod
    def get_match_summary(self, match_id: str) -> dict:
        """
        Get aggregated match summary metrics.
        
        Args:
            match_id: Match identifier
            
        Returns:
            Summary dictionary with possession, shots, distance, etc.
        """
        pass
