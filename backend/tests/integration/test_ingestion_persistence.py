"""
Integration tests for Ingestion Persistence.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.entities.match import Match
from src.domain.entities.event import Event
from src.infrastructure.db.database import Base
from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
from src.infrastructure.db.models import MatchModel, EventModel


@pytest.fixture
def test_db_session():
    """Create a test database session with in-memory SQLite."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


def test_ingestion_persistence_flow(test_db_session):
    """
    Integration test for full ingestion persistence flow.
    
    Tests:
    1. Create a Match entity with events
    2. Save to database
    3. Query database to verify persistence
    """
    # Arrange
    repo = PostgresMatchRepo(session=test_db_session)
    
    match = Match(
        match_id="sb_12345",
        events=[
            Event(event_type="Pass", timestamp=0.5, x=10.0, y=20.0),
            Event(event_type="Shot", timestamp=1.2, x=95.0, y=40.0),
            Event(event_type="Carry", timestamp=2.0, x=50.0, y=30.0)
        ]
    )
    
    # Act
    repo.save(match)
    
    # Assert - Verify match was saved
    saved_match = test_db_session.query(MatchModel).filter_by(match_id="sb_12345").first()
    assert saved_match is not None
    assert saved_match.match_id == "sb_12345"
    
    # Assert - Verify events were saved
    saved_events = test_db_session.query(EventModel).filter_by(match_id="sb_12345").all()
    assert len(saved_events) == 3
    assert saved_events[0].event_type == "Pass"
    assert saved_events[1].event_type == "Shot"
    assert saved_events[2].event_type == "Carry"


def test_idempotent_save(test_db_session):
    """Test that saving the same match twice doesn't create duplicates."""
    # Arrange
    repo = PostgresMatchRepo(session=test_db_session)
    match = Match(match_id="sb_99999", events=[])
    
    # Act
    repo.save(match)
    repo.save(match)  # Save again
    
    # Assert - Should only have one match
    match_count = test_db_session.query(MatchModel).filter_by(match_id="sb_99999").count()
    assert match_count == 1
