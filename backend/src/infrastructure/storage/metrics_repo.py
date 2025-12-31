"""
Metrics Repository Implementation - Infrastructure Layer

Concrete implementation of MetricsRepository port (in-memory for development).
"""
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
import numpy as np
from datetime import datetime

from src.domain.ports.metrics_repository import MetricsRepository as MetricsRepositoryPort


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


class MetricsRepository(MetricsRepositoryPort):
    """
    Concrete implementation of MetricsRepository port.
    Currently in-memory implementation for development.
    """
    
    
    def __init__(self, bucket: str = "metrics-data"):
        """Initialize with MinIO persistence."""
        self.pitch_control_frames: List[StoredPitchControlFrame] = []
        self.physical_stats: List[StoredPhysicalStats] = []
        self.ppda_metrics: List[StoredPPDA] = []
        self.bucket = bucket
        
        # Lazy load MinIO adapter only when needed to avoid init loop
        self._minio = None
        
    @property
    def minio(self):
        if not self._minio:
            from src.infrastructure.storage.minio_adapter import MinIOAdapter
            self._minio = MinIOAdapter(bucket=self.bucket)
        return self._minio

    def flush(self, match_id: str) -> None:
        """Persist current state to MinIO for the given match."""
        data = {
            "physical_stats": [asdict(s) for s in self.physical_stats if s.match_id == match_id],
            "ppda_metrics": [asdict(s) for s in self.ppda_metrics if s.match_id == match_id],
            # Note: Pitch control is too large for single JSON, usually handled separately or omitted from summary persistence
        }
        
        # Convert datetime to string
        def default(o):
            if isinstance(o, (datetime, np.datetime64)):
                return o.isoformat()
            if isinstance(o, np.ndarray):
                return o.tolist()
            if isinstance(o, np.generic):
                return o.item()
            raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

        json_bytes = json.dumps(data, default=default).encode('utf-8')
        
        key = f"metrics/{match_id}.json"
        self.minio.put_object(key, json_bytes, content_type="application/json")
        
    def load(self, match_id: str) -> None:
        """Load state from MinIO for the match."""
        key = f"metrics/{match_id}.json"
        try:
            data_bytes = self.minio.get_object(key)
            data = json.loads(data_bytes.decode('utf-8'))
            
            # Rehydrate StoredPhysicalStats
            self.physical_stats = [
                StoredPhysicalStats(**{**item, 'timestamp': datetime.fromisoformat(item['timestamp'])}) 
                for item in data.get("physical_stats", [])
            ]
            
            # Rehydrate StoredPPDA
            self.ppda_metrics = [
                StoredPPDA(**{**item, 'timestamp': datetime.fromisoformat(item['timestamp'])}) 
                for item in data.get("ppda_metrics", [])
            ]
            
        except Exception as e:
            # If not found, assume empty
            pass
    
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
    
    def get_physical_stats(self, match_id: str, team_id: str = None) -> List[dict]:
        """Get all physical stats for a match as dictionaries."""
        stats = [s for s in self.physical_stats if s.match_id == match_id]
        # Note: team_id filtering would require team information stored with players
        return [
            {
                "player_id": s.player_id,
                "total_distance": s.total_distance,
                "max_speed": s.max_speed,
                "sprint_count": s.sprint_count,
                "avg_speed": s.avg_speed
            }
            for s in stats
        ]
    
    def get_ppda(self, match_id: str, team_id: str) -> dict:
        """Get PPDA metrics for a team."""
        for p in self.ppda_metrics:
            if p.match_id == match_id and p.team_id == team_id:
                return {
                    "team_id": p.team_id,
                    "passes_allowed": p.passes_allowed,
                    "defensive_actions": p.defensive_actions,
                    "ppda": p.ppda
                }
        return {}
    
    def get_match_summary(self, match_id: str) -> dict:
        """
        Get aggregated match summary metrics.
        
        Aggregates physical stats and PPDA into a summary.
        """
        # Ensure data is loaded
        if not self.physical_stats or not any(s.match_id == match_id for s in self.physical_stats):
            self.load(match_id)
            
        physical = self.get_physical_stats(match_id)
        
        # Calculate totals
        total_distance = sum(p["total_distance"] for p in physical) if physical else 0
        max_speed = max((p["max_speed"] for p in physical), default=0)
        total_sprints = sum(p["sprint_count"] for p in physical) if physical else 0
        
        # Get PPDA for both teams
        home_ppda = self.get_ppda(match_id, "home")
        away_ppda = self.get_ppda(match_id, "away")
        
        return {
            "total_distance_km": round(total_distance, 2),
            "max_speed_kmh": round(max_speed, 1),
            "total_sprints": total_sprints,
            "players_tracked": len(physical),
            "home_ppda": home_ppda.get("ppda", 0),
            "away_ppda": away_ppda.get("ppda", 0)
        }
    
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
