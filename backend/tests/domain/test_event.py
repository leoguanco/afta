"""
TDD Tests for Event Entity.

Tests the Event dataclass and EventType enum.
"""

import pytest
from src.domain.entities.event import Event, EventType
from src.domain.value_objects.coordinates import Coordinates


class TestEventType:
    """Test EventType enum."""

    def test_pass_type_exists(self):
        """EventType should have PASS variant."""
        assert EventType.PASS.value == "pass"

    def test_shot_type_exists(self):
        """EventType should have SHOT variant."""
        assert EventType.SHOT.value == "shot"

    def test_carry_type_exists(self):
        """EventType should have CARRY variant."""
        assert EventType.CARRY.value == "carry"


class TestEvent:
    """Test Event entity."""

    def test_create_event(self):
        """Should create an Event with all required fields."""
        coords = Coordinates(x=52.5, y=34.0)
        event = Event(
            event_id="evt_001",
            event_type=EventType.PASS,
            timestamp=10.5,
            coordinates=coords,
            player_id="player_123",
        )
        assert event.event_id == "evt_001"
        assert event.event_type == EventType.PASS
        assert event.timestamp == 10.5
        assert event.coordinates.x == 52.5
        assert event.player_id == "player_123"

    def test_event_is_immutable(self):
        """Event should be immutable (frozen dataclass)."""
        coords = Coordinates(x=52.5, y=34.0)
        event = Event(
            event_id="evt_001",
            event_type=EventType.PASS,
            timestamp=10.5,
            coordinates=coords,
            player_id="player_123",
        )
        with pytest.raises(AttributeError):
            event.event_type = EventType.SHOT
