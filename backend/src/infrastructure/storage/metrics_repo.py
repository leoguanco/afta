"""
Metrics Repository - Infrastructure Layer

In-memory storage for calculated tactical metrics.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import numpy as np
from datetime import datetime


@dataclass
class StoredPitchControlFrame:
    """Stored pitch control data for a single frame."""
    match_id: str
    frame_id: int
    home_control: np.ndarray
    away_control: np.ndarray
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StoredPhysicalStats:
    """Stored physical statistics for a player."""
    match_id: str
    player_id: str
    total_distance: float
    max_speed: float
    sprint_count: int
    avg_speed: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class StoredPPDA:
    """Stored PPDA metrics."""
    match_id: str
    team_id: str
    passes_allowed: int
    defensive_actions: int
    ppda: float
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsRepository:
    """
    Repository for storing and retrieving tactical metrics.
    Currently in-memory implementation for development.
    """
    
    def __init__(self):
        """Initialize in-memory storage."""
        self.pitch_control_frames: List[StoredPitchControlFrame] = []
        self.physical_stats: List[StoredPhysicalStats] = []
        self.ppda_metrics: List[StoredPPDA] = []
    
    def save_pitch_control_frame(
        self,
        match_id: str,
        frame_id: int,
        home_control: np.ndarray,
        away_control: np.ndarray
    ) -> None:
        """
        Save pitch control grid for a frame.
        
        Args:
            match_id: Match identifier
            frame_id: Frame number
            home_control: Home team control grid
            away_control: Away team control grid
        """
        frame = StoredPitchControlFrame(
            match_id=match_id,
            frame_id=frame_id,
            home_control=home_control.copy(),
            away_control=away_control.copy()
        )
        self.pitch_control_frames.append(frame)
    
    def save_physical_stats(
        self,
        match_id: str,
        player_id: str,
        total_distance: float,
        max_speed: float,
        sprint_count: int,
        avg_speed: float
    ) -> None:
        """
        Save physical statistics for a player.
        
        Args:
            match_id: Match identifier
            player_id: Player identifier
            total_distance: Total distance covered (km)
            max_speed: Maximum speed (km/h)
            sprint_count: Number of sprints
            avg_speed: Average speed (km/h)
        """
        stats = StoredPhysicalStats(
            match_id=match_id,
            player_id=player_id,
            total_distance=total_distance,
            max_speed=max_speed,
            sprint_count=sprint_count,
            avg_speed=avg_speed
        )
        self.physical_stats.append(stats)
    
    def save_ppda(
        self,
        match_id: str,
        team_id: str,
        passes_allowed: int,
        defensive_actions: int,
        ppda: float
    ) -> None:
        """
        Save PPDA metrics for a team.
        
        Args:
            match_id: Match identifier
            team_id: Team identifier
            passes_allowed: Number of opposition passes allowed
            defensive_actions: Number of defensive actions
            ppda: Calculated PPDA value
        """
        metric = StoredPPDA(
            match_id=match_id,
            team_id=team_id,
            passes_allowed=passes_allowed,
            defensive_actions=defensive_actions,
            ppda=ppda
        )
        self.ppda_metrics.append(metric)
    
    def get_pitch_control_frames(self, match_id: str) -> List[StoredPitchControlFrame]:
        """Get all pitch control frames for a match."""
        return [f for f in self.pitch_control_frames if f.match_id == match_id]
    
    def get_physical_stats(self, match_id: str) -> List[StoredPhysicalStats]:
        """Get all physical stats for a match."""
        return [s for s in self.physical_stats if s.match_id == match_id]
    
    def get_ppda_metrics(self, match_id: str) -> List[StoredPPDA]:
        """Get all PPDA metrics for a match."""
        return [p for p in self.ppda_metrics if p.match_id == match_id]
    
    def clear_match_data(self, match_id: str) -> None:
        """Clear all data for a specific match."""
        self.pitch_control_frames = [
            f for f in self.pitch_control_frames if f.match_id != match_id
        ]
        self.physical_stats = [
            s for s in self.physical_stats if s.match_id != match_id
        ]
        self.ppda_metrics = [
            p for p in self.ppda_metrics if p.match_id != match_id
        ]
