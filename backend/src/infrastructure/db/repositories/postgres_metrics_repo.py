"""
PostgresMetricsRepository - Infrastructure Layer

Postgres implementation of MetricsRepository port.
"""
import logging
from typing import List, Dict, Optional
import numpy as np

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.domain.ports.metrics_repository import MetricsRepository as MetricsRepositoryPort
from src.infrastructure.db.database import SessionLocal
from src.infrastructure.db.models import PhysicalStatsModel, PPDAStatsModel

logger = logging.getLogger(__name__)


class PostgresMetricsRepository(MetricsRepositoryPort):
    """
    Postgres implementation of MetricsRepository.
    
    Uses SQLAlchemy ORM with upsert semantics for save operations.
    """
    
    def __init__(self, session: Optional[Session] = None):
        """
        Initialize with optional session.
        
        Args:
            session: Optional SQLAlchemy session (if None, creates new one)
        """
        self._session = session
        self._owns_session = session is None
    
    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = SessionLocal()
        return self._session
    
    def close(self):
        """Close session if we own it."""
        if self._owns_session and self._session:
            self._session.close()
            self._session = None
    
    def save_pitch_control_frame(
        self,
        match_id: str,
        frame_id: int,
        home_control: np.ndarray,
        away_control: np.ndarray
    ) -> None:
        """
        Pitch control frames are NOT persisted to Postgres.
        
        They are large arrays better suited for object storage or specialized
        time-series databases. This method logs a warning and no-ops.
        """
        logger.debug(f"Pitch control frame {frame_id} for {match_id} not persisted (by design)")
    
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
        Save physical statistics for a player using upsert.
        """
        stmt = pg_insert(PhysicalStatsModel).values(
            match_id=match_id,
            player_id=player_id,
            total_distance=total_distance,
            max_speed=max_speed,
            sprint_count=sprint_count,
            avg_speed=avg_speed
        )
        
        # On conflict, update the values
        stmt = stmt.on_conflict_do_update(
            index_elements=['match_id', 'player_id'],
            set_={
                'total_distance': stmt.excluded.total_distance,
                'max_speed': stmt.excluded.max_speed,
                'sprint_count': stmt.excluded.sprint_count,
                'avg_speed': stmt.excluded.avg_speed
            }
        )
        
        self.session.execute(stmt)
        self.session.commit()
    
    def save_ppda(
        self,
        match_id: str,
        team_id: str,
        passes_allowed: int,
        defensive_actions: int,
        ppda: float
    ) -> None:
        """
        Save PPDA metrics for a team using upsert.
        """
        stmt = pg_insert(PPDAStatsModel).values(
            match_id=match_id,
            team_id=team_id,
            passes_allowed=passes_allowed,
            defensive_actions=defensive_actions,
            ppda=ppda
        )
        
        stmt = stmt.on_conflict_do_update(
            index_elements=['match_id', 'team_id'],
            set_={
                'passes_allowed': stmt.excluded.passes_allowed,
                'defensive_actions': stmt.excluded.defensive_actions,
                'ppda': stmt.excluded.ppda
            }
        )
        
        self.session.execute(stmt)
        self.session.commit()
    
    def get_physical_stats(self, match_id: str, team_id: str = None) -> List[dict]:
        """
        Get physical statistics for a match.
        """
        query = self.session.query(PhysicalStatsModel).filter(
            PhysicalStatsModel.match_id == match_id
        )
        
        if team_id:
            query = query.filter(PhysicalStatsModel.team_id == team_id)
        
        results = query.all()
        
        return [
            {
                "player_id": r.player_id,
                "total_distance": r.total_distance,
                "max_speed": r.max_speed,
                "sprint_count": r.sprint_count,
                "avg_speed": r.avg_speed
            }
            for r in results
        ]
    
    def get_ppda(self, match_id: str, team_id: str) -> dict:
        """
        Get PPDA metrics for a team.
        """
        result = self.session.query(PPDAStatsModel).filter(
            PPDAStatsModel.match_id == match_id,
            PPDAStatsModel.team_id == team_id
        ).first()
        
        if not result:
            return {}
        
        return {
            "team_id": result.team_id,
            "passes_allowed": result.passes_allowed,
            "defensive_actions": result.defensive_actions,
            "ppda": result.ppda
        }
    
    def get_match_summary(self, match_id: str) -> dict:
        """
        Get aggregated match summary metrics.
        """
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
    
    def flush(self, match_id: str = None) -> None:
        """
        No-op for compatibility with existing task code.
        
        Postgres commits are done immediately in save methods.
        """
        pass
    
    def load(self, match_id: str) -> None:
        """
        No-op for compatibility with existing task code.
        
        Postgres data is fetched on-demand in get methods.
        """
        pass
