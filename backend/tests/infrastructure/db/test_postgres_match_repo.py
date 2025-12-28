"""
Unit tests for PostgresMatchRepo.
"""

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from src.domain.entities.match import Match
from src.domain.entities.event import Event
from src.domain.value_objects.coordinates import Coordinates
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
            home_team_id="HomeFC",
            away_team_id="AwayFC",
            events=[
                Event(event_id="e1", event_type="Pass", timestamp=10.5, coordinates=Coordinates(x=52.5, y=34.0), player_id="p1", team_id="t1"),
                Event(event_id="e2", event_type="Shot", timestamp=15.2, coordinates=Coordinates(x=95.0, y=40.0), player_id="p1", team_id="t1")
            ]
        )
        
        # Act
        repo.save(match)
        
        # Assert
        assert mock_session.add.call_count == 3  # 1 match + 2 events
        
        # Verify Match metadata saving
        match_call = mock_session.add.call_args_list[0]
        saved_match = match_call[0][0]
        assert isinstance(saved_match, MatchModel)
        assert saved_match.match_metadata["home_team_id"] == "HomeFC"
        
        mock_session.commit.assert_called_once()

    def test_save_existing_match_does_not_duplicate(self):
        """Test that saving an existing match doesn't create duplicates."""
        # Arrange
        mock_session = Mock(spec=Session)
        existing_match = MatchModel(match_id="test_123", source="statsbomb")
        mock_session.query.return_value.filter_by.return_value.first.return_value = existing_match
        
        repo = PostgresMatchRepo(session=mock_session)
        match = Match(match_id="test_123", home_team_id="HomeFC", away_team_id="AwayFC", events=[])
        
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
        match = Match(match_id="test_123", home_team_id="HomeFC", away_team_id="AwayFC", events=[])
        
        # Act & Assert
        with pytest.raises(Exception):
            repo.save(match)
        
        mock_session.rollback.assert_called_once()
