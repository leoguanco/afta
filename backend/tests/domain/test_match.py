"""
TDD Tests for Match Aggregate Root.
"""

import pytest
from src.domain.entities.match import Match
from src.domain.entities.event import Event, EventType
from src.domain.value_objects.coordinates import Coordinates


class TestMatch:
    """Test Match aggregate root."""

    def test_create_match(self):
        """Should create a Match with metadata."""
        match = Match(
            match_id="match_001",
            home_team_id="team_a",
            away_team_id="team_b",
            competition="La Liga",
            season="2023/2024",
        )
        assert match.match_id == "match_001"
        assert match.home_team_id == "team_a"
        assert match.away_team_id == "team_b"
        assert len(match.events) == 0

    def test_add_event(self):
        """Should be able to add events to a match."""
        match = Match(
            match_id="match_001",
            home_team_id="team_a",
            away_team_id="team_b",
        )
        event = Event(
            event_id="evt_001",
            event_type=EventType.PASS,
            timestamp=10.5,
            coordinates=Coordinates(x=52.5, y=34.0),
            player_id="player_123",
        )
        match.add_event(event)
        assert len(match.events) == 1
        assert match.events[0].event_id == "evt_001"

    def test_get_events_by_type(self):
        """Should filter events by type."""
        match = Match(
            match_id="match_001",
            home_team_id="team_a",
            away_team_id="team_b",
        )
        match.add_event(Event(
            event_id="evt_001",
            event_type=EventType.PASS,
            timestamp=10.0,
            coordinates=Coordinates(x=50.0, y=30.0),
            player_id="p1",
        ))
        match.add_event(Event(
            event_id="evt_002",
            event_type=EventType.SHOT,
            timestamp=20.0,
            coordinates=Coordinates(x=90.0, y=34.0),
            player_id="p1",
        ))
        shots = match.get_events_by_type(EventType.SHOT)
        assert len(shots) == 1
        assert shots[0].event_type == EventType.SHOT
