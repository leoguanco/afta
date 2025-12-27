"""
Unit tests for Tactical Metrics Domain Entities.
"""
import pytest
import numpy as np

from src.domain.entities.player_trajectory import (
    PlayerTrajectory,
    FramePosition,
    PhysicalMetrics
)
from src.domain.entities.match_frame import (
    MatchFrame,
    PlayerPosition,
    BallPosition
)
from src.domain.entities.tactical_match import (
    TacticalMatch,
    MatchEvent,
    EventType
)


class TestPlayerTrajectory:
    """Tests for PlayerTrajectory entity."""
    
    def test_constant_velocity(self):
        """Test calculation with constant velocity."""
        frames = [
            FramePosition(i, float(i), 0.0, i / 25.0)
            for i in range(100)
        ]
        
        trajectory = PlayerTrajectory("player1", frames)
        metrics = trajectory.calculate_physical_metrics()
        
        assert metrics.total_distance > 0.0
        assert metrics.max_speed > 0.0
    
    def test_stationary_player(self):
        """Test with stationary player."""
        frames = [
            FramePosition(i, 10.0, 10.0, i / 25.0)
            for i in range(50)
        ]
        
        trajectory = PlayerTrajectory("player1", frames)
        metrics = trajectory.calculate_physical_metrics()
        
        assert metrics.total_distance == pytest.approx(0.0, abs=0.1)
        assert metrics.max_speed == pytest.approx(0.0, abs=1.0)
        assert metrics.sprint_count == 0
    
    def test_sprint_detection(self):
        """Test sprint detection."""
        frames = [
            FramePosition(i, float(i * 10), 0.0, i / 25.0)
            for i in range(50)
        ]
        
        trajectory = PlayerTrajectory("player1", frames, sprint_threshold=25.0)
        sprints = trajectory.detect_sprints()
        
        assert len(sprints) > 0


class TestMatchFrame:
    """Tests for MatchFrame entity."""
    
    def test_pitch_control_grid_shape(self):
        """Test that pitch control grid has correct shape."""
        players = [
            PlayerPosition("p1", "home", 50.0, 30.0),
            PlayerPosition("p2", "away", 55.0, 35.0)
        ]
        ball = BallPosition(52.5, 34.0)
        
        frame = MatchFrame(1, players, ball, grid_width=32, grid_height=24)
        result = frame.calculate_pitch_control()
        
        assert result.home_control.shape == (24, 32)
        assert result.away_control.shape == (24, 32)
    
    def test_control_values_range(self):
        """Test that control values are in [0, 1]."""
        players = [
            PlayerPosition("p1", "home", 50.0, 30.0),
            PlayerPosition("p2", "away", 55.0, 35.0)
        ]
        ball = BallPosition(52.5, 34.0)
        
        frame = MatchFrame(1, players, ball)
        result = frame.calculate_pitch_control()
        
        assert np.all(result.home_control >= 0.0)
        assert np.all(result.home_control <= 1.0)
        assert np.all(result.away_control >= 0.0)
        assert np.all(result.away_control <= 1.0)
    
    def test_team_dominance(self):
        """Test team dominance calculation."""
        players = [
            PlayerPosition("h1", "home", 50.0, 30.0),
            PlayerPosition("h2", "home", 52.0, 32.0),
            PlayerPosition("a1", "away", 80.0, 50.0),
        ]
        ball = BallPosition(52.5, 34.0)
        
        frame = MatchFrame(1, players, ball)
        dominance = frame.get_team_dominance()
        
        assert dominance["home"] > dominance["away"]


class TestTacticalMatch:
    """Tests for TacticalMatch entity."""
    
    def test_ppda_calculation(self):
        """Test PPDA calculation."""
        events = [
            MatchEvent("e1", EventType.PASS, "home", "p1", 10.0, 60.0, 30.0),
            MatchEvent("e2", EventType.PASS, "home", "p1", 15.0, 65.0, 32.0),
            MatchEvent("e3", EventType.PASS, "home", "p1", 20.0, 70.0, 34.0),
            MatchEvent("e4", EventType.TACKLE, "away", "p2", 25.0, 72.0, 33.0),
        ]
        
        match = TacticalMatch("match1", events)
        ppda = match.calculate_ppda("away", "home")
        
        assert ppda.passes_allowed == 3
        assert ppda.defensive_actions == 1
        assert ppda.ppda == pytest.approx(3.0)
    
    def test_pressing_metrics(self):
        """Test pressing metrics by zones."""
        events = [
            MatchEvent("e1", EventType.PRESSURE, "home", "p1", 10.0, 20.0, 30.0),
            MatchEvent("e2", EventType.PRESSURE, "home", "p2", 15.0, 50.0, 35.0),
            MatchEvent("e3", EventType.PRESSURE, "home", "p3", 20.0, 90.0, 40.0),
        ]
        
        match = TacticalMatch("match1", events)
        metrics = match.calculate_pressing_metrics("home")
        
        assert metrics.defensive_third_presses == 1
        assert metrics.middle_third_presses == 1
        assert metrics.attacking_third_presses == 1
        assert metrics.total_presses == 3
