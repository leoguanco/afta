"""
PostgreSQL implementation of MatchRepository port.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from src.domain.entities.match import Match
from src.domain.entities.event import Event, EventType
from src.domain.value_objects.coordinates import Coordinates
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

    def get_match(self, match_id: str, source: Optional[str] = None) -> Optional[Match]:
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
            
            # Reconstruct Event entities from EventModel
            events = []
            for event_model in match_model.events:
                # Convert event_type string to EventType enum
                try:
                    event_type = EventType(event_model.event_type)
                except ValueError:
                    # Skip events with unknown types
                    continue
                
                # Create Coordinates value object
                coordinates = Coordinates(x=event_model.x, y=event_model.y)
                
                # Reconstruct Event entity
                event = Event(
                    event_id=str(event_model.id),
                    event_type=event_type,
                    timestamp=event_model.timestamp,
                    coordinates=coordinates,
                    player_id=event_model.event_metadata.get("player_id", "unknown") if event_model.event_metadata else "unknown",
                    team_id=event_model.event_metadata.get("team_id") if event_model.event_metadata else None
                )
                events.append(event)
            
            # Reconstruct Match aggregate
            return Match(
                match_id=match_model.match_id,
                home_team_id=match_model.match_metadata.get("home_team_id", "unknown") if match_model.match_metadata else "unknown",
                away_team_id=match_model.match_metadata.get("away_team_id", "unknown") if match_model.match_metadata else "unknown",
                events=events
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
                # Create new match with metadata
                match_metadata = {
                    "home_team_id": match.home_team_id,
                    "away_team_id": match.away_team_id,
                }
                if match.competition:
                    match_metadata["competition"] = match.competition
                if match.season:
                    match_metadata["season"] = match.season
                if match.match_date:
                    match_metadata["match_date"] = match.match_date
                
                match_model = MatchModel(
                    match_id=match.match_id,
                    source="statsbomb",  # Default source, can be overridden via Match metadata if needed
                    match_metadata=match_metadata
                )
                session.add(match_model)
                
                # Create events
                for event in match.events:
                    event_metadata = {
                        "player_id": event.player_id,
                    }
                    if event.team_id:
                        event_metadata["team_id"] = event.team_id
                    if event.end_coordinates:
                        event_metadata["end_x"] = event.end_coordinates.x
                        event_metadata["end_y"] = event.end_coordinates.y
                    
                    event_model = EventModel(
                        match_id=match.match_id,
                        event_type=event.event_type.value if hasattr(event.event_type, 'value') else event.event_type,
                        timestamp=event.timestamp,
                        x=event.coordinates.x,
                        y=event.coordinates.y,
                        event_metadata=event_metadata
                    )
                    session.add(event_model)
            
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if not self.session:
                session.close()

    def list_matches(self, limit: int = 20, offset: int = 0) -> List[Match]:
        """
        List all matches from the database.
        
        Args:
            limit: Maximum number of matches to return.
            offset: Number of matches to skip (for pagination).
        
        Returns:
            List of Match domain entities.
        """
        session = self.session or SessionLocal()
        try:
            match_models = (
                session.query(MatchModel)
                .order_by(MatchModel.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            
            matches = []
            for match_model in match_models:
                # Get event count without loading all events
                event_count = session.query(EventModel).filter_by(
                    match_id=match_model.match_id
                ).count()
                
                # Create lightweight Match object
                match = Match(
                    match_id=match_model.match_id,
                    home_team_id=match_model.match_metadata.get("home_team_id", "Unknown") if match_model.match_metadata else "Unknown",
                    away_team_id=match_model.match_metadata.get("away_team_id", "Unknown") if match_model.match_metadata else "Unknown",
                    events=[None] * event_count  # Placeholder to get event count
                )
                matches.append(match)
            
            return matches
        finally:
            if not self.session:
                session.close()
