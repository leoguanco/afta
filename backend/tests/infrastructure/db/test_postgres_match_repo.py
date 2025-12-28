"""
Unit tests for PostgresMatchRepo.
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from src.domain.entities.match import Match
from src.domain.entities.event import Event
from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
from src.infrastructure.db.models import MatchModel, EventModel


class TestPostgresMatchRepo:
    """Test suite for PostgresMatchRepo."""

    def test_save_new_match(self):
        """Test saving a new match to the database."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        repo = PostgresMatchRepo(session=mock_session)
        
        match = Match(
            match_id="test_123",
            events=[
                Event(event_type="Pass", timestamp=10.5, x=52.5, y=34.0),
                Event(event_type="Shot", timestamp=15.2, x=95.0, y=40.0)
            ]
        )
        
        # Act
        repo.save(match)
        
        # Assert
        assert mock_session.add.call_count == 3  # 1 match + 2 events
        mock_session.commit.assert_called_once()

    def test_save_existing_match_does_not_duplicate(self):
        """Test that saving an existing match doesn't create duplicates."""
        # Arrange
        mock_session = Mock(spec=Session)
        existing_match = MatchModel(match_id="test_123", source="statsbomb")
        mock_session.query.return_value.filter_by.return_value.first.return_value = existing_match
        
        repo = PostgresMatchRepo(session=mock_session)
        match = Match(match_id="test_123", events=[])
        
        # Act
        repo.save(match)
        
        # Assert
        # Should commit but not add new records
        mock_session.commit.assert_called_once()

    def test_save_rolls_back_on_error(self):
        """Test that save rolls back transaction on error."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_session.commit.side_effect = Exception("DB Error")
        
        repo = PostgresMatchRepo(session=mock_session)
        match = Match(match_id="test_123", events=[])
        
        # Act & Assert
        with pytest.raises(Exception):
            repo.save(match)
        
        mock_session.rollback.assert_called_once()
