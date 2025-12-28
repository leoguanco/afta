"""
PostgreSQL implementation of MatchRepository port.
"""

from typing import Optional
from sqlalchemy.orm import Session

from src.domain.entities.match import Match
from src.domain.ports.match_repository import MatchRepository
from src.infrastructure.db.database import SessionLocal
from src.infrastructure.db.models import MatchModel, EventModel


class PostgresMatchRepo(MatchRepository):
    """
    PostgreSQL adapter for MatchRepository.
    
    Implements persistence using SQLAlchemy ORM.
    """

    def __init__(self, session: Optional[Session] = None):
        """
        Initialize repository with optional session.
        
        Args:
            session: SQLAlchemy session. If None, creates a new session per operation.
        """
        self.session = session

    def get_match(self, match_id: str, source: str) -> Optional[Match]:
        """
        Fetch a match from PostgreSQL.
        
        Args:
            match_id: Unique identifier for the match.
            source: Not used in DB retrieval (only for external adapters).
        
        Returns:
            Match domain entity if found, None otherwise.
        """
        session = self.session or SessionLocal()
        try:
            match_model = session.query(MatchModel).filter_by(match_id=match_id).first()
            if not match_model:
                return None
            
            # Map DB model to Domain entity
            # Note: This is a simplified mapping. In production, you'd reconstruct full Event objects
            return Match(
                match_id=match_model.match_id,
                events=[]  # TODO: Reconstruct Event entities from EventModel
            )
        finally:
            if not self.session:
                session.close()

    def save(self, match: Match) -> None:
        """
        Persist a Match aggregate to PostgreSQL.
        
        Args:
            match: The Match domain entity to save.
        """
        session = self.session or SessionLocal()
        try:
            # Check if match already exists
            existing = session.query(MatchModel).filter_by(match_id=match.match_id).first()
            
            if existing:
                # Update existing match (or skip to maintain idempotency)
                pass
            else:
                # Create new match
                match_model = MatchModel(
                    match_id=match.match_id,
                    source="statsbomb",  # TODO: Get from match metadata
                    metadata={}
                )
                session.add(match_model)
                
                # Create events
                for event in match.events:
                    event_model = EventModel(
                        match_id=match.match_id,
                        event_type=event.event_type,
                        timestamp=event.timestamp,
                        x=event.x,
                        y=event.y,
                        metadata={}
                    )
                    session.add(event_model)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if not self.session:
                session.close()
