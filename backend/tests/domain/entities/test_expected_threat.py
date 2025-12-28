"""
TDD Tests for Expected Threat (xT) Calculation.

Tests for xT grid value objects and TacticalMatch xT calculations.
"""
import pytest
from src.domain.value_objects.expected_threat_grid import ExpectedThreatGrid
from src.domain.entities.tactical_match import TacticalMatch, MatchEvent, EventType


class TestExpectedThreatGrid:
    """Test suite for xT grid value object."""

    def test_grid_has_correct_dimensions(self):
        """xT grid should have 12x8 zones by default."""
        grid = ExpectedThreatGrid()
        
        assert grid.width == 12
        assert grid.height == 8

    def test_goal_zone_has_highest_threat(self):
        """The zone in front of goal should have highest xT value."""
        grid = ExpectedThreatGrid()
        
        # Bottom right corner (opponent's goal area)
        goal_zone_value = grid.get_threat(11, 3)  # Near center of goal
        midfield_value = grid.get_threat(6, 4)    # Midfield
        
        assert goal_zone_value > midfield_value

    def test_own_half_has_low_threat(self):
        """Own half should have very low xT values."""
        grid = ExpectedThreatGrid()
        
        own_half_value = grid.get_threat(0, 4)  # Own half
        opponent_half_value = grid.get_threat(11, 4)  # Opponent half
        
        assert own_half_value < opponent_half_value

    def test_get_zone_from_pitch_coordinates(self):
        """Should convert pitch coordinates (0-105m, 0-68m) to grid zones."""
        grid = ExpectedThreatGrid()
        
        # Center of pitch (52.5m, 34m) should map to middle zone
        zone_x, zone_y = grid.pitch_to_zone(52.5, 34.0)
        
        assert zone_x == 6  # 12 zones / 2 = 6 (center)
        assert zone_y == 4  # 8 zones / 2 = 4 (center)

    def test_xt_difference_for_pass(self):
        """Should calculate xT gained/lost for a pass."""
        grid = ExpectedThreatGrid()
        
        # Pass from midfield to attacking third
        from_x, from_y = 52.5, 34.0  # Midfield center
        to_x, to_y = 90.0, 34.0      # Attacking third
        
        xt_gained = grid.calculate_xt_change(from_x, from_y, to_x, to_y)
        
        assert xt_gained > 0  # Forward pass should increase xT


class TestTacticalMatchXt:
    """Test xT calculation in TacticalMatch entity."""

    def test_calculate_xt_for_possession_chain(self):
        """Should calculate total xT accumulated in a possession sequence."""
        events = [
            MatchEvent(
                event_id="1",
                minute=10,
                team="home",
                player_id="player_1",
                event_type=EventType.PASS,
                start_x=30.0, start_y=34.0,
                end_x=52.5, end_y=34.0
            ),
            MatchEvent(
                event_id="2",
                minute=10,
                team="home",
                player_id="player_2",
                event_type=EventType.PASS,
                start_x=52.5, start_y=34.0,
                end_x=80.0, end_y=30.0
            ),
            MatchEvent(
                event_id="3",
                minute=10,
                team="home",
                player_id="player_3",
                event_type=EventType.SHOT,
                start_x=80.0, start_y=30.0,
                end_x=105.0, end_y=34.0
            ),
        ]
        
        match = TacticalMatch(
            match_id="test_123",
            home_team="home",
            away_team="away",
            events=events
        )
        
        # When: Calculate xT chain
        xt_chain = match.calculate_xt_chain("home")
        
        # Then: Total xT should be positive (progressed towards goal)
        assert xt_chain.total_xt > 0
        assert len(xt_chain.events) == 3

    def test_backward_pass_loses_xt(self):
        """A backward pass should have negative xT change."""
        events = [
            MatchEvent(
                event_id="1",
                minute=10,
                team="home",
                player_id="player_1",
                event_type=EventType.PASS,
                start_x=80.0, start_y=34.0,
                end_x=50.0, end_y=34.0  # Backward pass
            ),
        ]
        
        match = TacticalMatch(
            match_id="test_123",
            home_team="home",
            away_team="away",
            events=events
        )
        
        xt_chain = match.calculate_xt_chain("home")
        
        # Backward pass = negative xT
        assert xt_chain.total_xt < 0
