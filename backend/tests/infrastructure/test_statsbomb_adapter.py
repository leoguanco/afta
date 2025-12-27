"""
TDD Tests for StatsBomb Adapter.

Integration tests that verify the adapter can fetch and transform data.
"""

import pytest
from src.infrastructure.adapters.statsbomb_adapter import StatsBombAdapter


class TestStatsBombAdapter:
    """Integration tests for StatsBomb data fetching."""

    @pytest.fixture
    def adapter(self):
        """Create adapter instance."""
        return StatsBombAdapter()

    def test_get_match_returns_match(self, adapter):
        """Should fetch a match from StatsBomb open data."""
        # Match 3869519 is from the Women's World Cup 2019 (Sweden vs USA)
        match = adapter.get_match(match_id="3869519", source="statsbomb")
        assert match is not None
        assert match.match_id == "3869519"

    def test_match_has_events(self, adapter):
        """Fetched match should contain events."""
        match = adapter.get_match(match_id="3869519", source="statsbomb")
        assert len(match.events) > 0

    def test_events_have_normalized_coordinates(self, adapter):
        """Events should have coordinates in the 105x68 range."""
        match = adapter.get_match(match_id="3869519", source="statsbomb")
        for event in match.events[:10]:  # Check first 10 events
            assert 0 <= event.coordinates.x <= 105
            assert 0 <= event.coordinates.y <= 68
