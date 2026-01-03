"""
PostgresLineupRepository - Infrastructure Layer

SQLAlchemy implementation of LineupRepository port.
"""
from typing import List, Optional
import logging

from sqlalchemy.orm import Session
from sqlalchemy import delete

from src.domain.ports.lineup_repository import LineupRepository, PlayerMappingDTO
from src.infrastructure.db.database import get_session
from src.infrastructure.db.models import PlayerMappingModel

logger = logging.getLogger(__name__)


class PostgresLineupRepository(LineupRepository):
    """
    PostgreSQL implementation of LineupRepository.
    """
    
    def save_mappings(self, match_id: str, mappings: List[PlayerMappingDTO]) -> None:
        """
        Save player mappings for a match.
        
        Deletes existing and inserts new mappings (replace strategy).
        """
        db: Session = next(get_session())
        try:
            # Delete existing mappings
            db.query(PlayerMappingModel).filter(
                PlayerMappingModel.match_id == match_id
            ).delete()
            
            # Insert new mappings
            for mapping in mappings:
                model = PlayerMappingModel(
                    match_id=match_id,
                    track_id=mapping.track_id,
                    player_name=mapping.player_name,
                    jersey_number=mapping.jersey_number,
                    team=mapping.team
                )
                db.add(model)
            
            db.commit()
            logger.info(f"Saved {len(mappings)} player mappings for match {match_id}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save mappings for {match_id}: {e}")
            raise
        finally:
            db.close()
    
    def get_mappings(self, match_id: str) -> List[PlayerMappingDTO]:
        """Get all player mappings for a match."""
        db: Session = next(get_session())
        try:
            models = db.query(PlayerMappingModel).filter(
                PlayerMappingModel.match_id == match_id
            ).all()
            
            return [
                PlayerMappingDTO(
                    track_id=m.track_id,
                    player_name=m.player_name,
                    jersey_number=m.jersey_number,
                    team=m.team
                )
                for m in models
            ]
        finally:
            db.close()
    
    def get_player_name(self, match_id: str, track_id: int) -> Optional[str]:
        """Get player name by track ID."""
        db: Session = next(get_session())
        try:
            model = db.query(PlayerMappingModel).filter(
                PlayerMappingModel.match_id == match_id,
                PlayerMappingModel.track_id == track_id
            ).first()
            
            return model.player_name if model else None
        finally:
            db.close()
    
    def get_team(self, match_id: str, track_id: int) -> Optional[str]:
        """Get team by track ID."""
        db: Session = next(get_session())
        try:
            model = db.query(PlayerMappingModel).filter(
                PlayerMappingModel.match_id == match_id,
                PlayerMappingModel.track_id == track_id
            ).first()
            
            return model.team if model else None
        finally:
            db.close()
    
    def delete_mappings(self, match_id: str) -> None:
        """Delete all mappings for a match."""
        db: Session = next(get_session())
        try:
            deleted = db.query(PlayerMappingModel).filter(
                PlayerMappingModel.match_id == match_id
            ).delete()
            
            db.commit()
            logger.info(f"Deleted {deleted} mappings for match {match_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete mappings for {match_id}: {e}")
            raise
        finally:
            db.close()
