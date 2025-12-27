"""
Unit tests for Tactical Metrics Domain Services.
"""
import pytest
import numpy as np

from src.domain.services.physics import PhysicsService, FramePosition, PhysicalMetrics
from src.domain.services.pitch_control import (
    PitchControlService,
    PlayerPosition,
    PitchControlGrid
)
from src.domain.services.events import (
    TacticalEventsService,
    MatchEvent,
    EventType,
    PPDAResult,
    PressureMetrics
)


class TestPhysicsService:
    """Tests for PhysicsService."""
    
    def test_constant_velocity(self):
        """Test calculation with constant velocity (1 m/s)."""
        service = PhysicsService(fps=25.0)
        
        # Create frames with constant 1 m/s movement
        frames = [
            FramePosition(
                frame_id=i,
                player_id="player1",
                x=float(i),  # 1 meter per frame = 25 m/s at 25fps
                y=0.0,
                timestamp=i / 25.0
            )
            for i in range(100)
        ]
        
        metrics = service.calculate_metrics(frames)
        
        assert metrics.player_id == "player1"
        assert metrics.total_distance > 0.0
        assert metrics.max_speed > 0.0
    
    def test_stationary_player(self):
        """Test with stationary player (zero velocity)."""
        service = PhysicsService(fps=25.0)
        
        frames = [
            FramePosition(
                frame_id=i,
                player_id="player1",
                x=10.0,
                y=10.0,
                timestamp=i / 25.0
            )
            for i in range(50)
        ]
        
        metrics = service.calculate_metrics(frames)
        
        assert metrics.total_distance == pytest.approx(0.0, abs=0.1)
        assert metrics.max_speed == pytest.approx(0.0, abs=1.0)
        assert metrics.sprint_count == 0
    
    def test_sprint_detection(self):
        """Test sprint detection above threshold."""
        service = PhysicsService(fps=25.0, sprint_threshold=25.0)
        
        # Create frames with high velocity (sprint)
        # 10 meters per frame at 25fps = 250 m/s = 900 km/h (intentionally high)
        frames = [
            FramePosition(
                frame_id=i,
                player_id="player1",
                x=float(i * 10),
                y=0.0,
                timestamp=i / 25.0
            )
            for i in range(50)
        ]
        
        metrics = service.calculate_metrics(frames)
        
        # Should detect sprints
        assert metrics.sprint_count > 0
        assert metrics.max_speed > service.sprint_threshold


class TestPitchControlService:
    """Tests for PitchControlService."""
    
    def test_grid_shape(self):
        """Test that output grid has correct shape."""
        service = PitchControlService(grid_width=32, grid_height=24)
        
        players = [
            PlayerPosition("p1", "home", 50.0, 30.0),
            PlayerPosition("p2", "away", 55.0, 35.0)
        ]
        
        result = service.calculate_pitch_control(players, ball_x=52.5, ball_y=34.0)
        
        assert result.home_control.shape == (24, 32)
        assert result.away_control.shape == (24, 32)
    
    def test_control_values_range(self):
        """Test that control values are in [0, 1] range."""
        service = PitchControlService()
        
        players = [
            PlayerPosition("p1", "home", 50.0, 30.0),
            PlayerPosition("p2", "away", 55.0, 35.0)
        ]
        
        result = service.calculate_pitch_control(players, ball_x=52.5, ball_y=34.0)
        
        assert np.all(result.home_control >= 0.0)
        assert np.all(result.home_control <= 1.0)
        assert np.all(result.away_control >= 0.0)
        assert np.all(result.away_control <= 1.0)
    
    def test_team_dominance(self):
        """Test that team with more players near ball has higher control."""
        service = PitchControlService()
        
        # Home team has many players near center
        players = [
            PlayerPosition("h1", "home", 50.0, 30.0),
            PlayerPosition("h2", "home", 52.0, 32.0),
            PlayerPosition("h3", "home", 54.0, 34.0),
            PlayerPosition("a1", "away", 80.0, 50.0),  # Far away
        ]
        
        result = service.calculate_pitch_control(players, ball_x=52.5, ball_y=34.0)
        
        # Home should have higher average control
        assert np.mean(result.home_control) > np.mean(result.away_control)


class TestTacticalEventsService:
    """Tests for TacticalEventsService."""
    
    def test_ppda_calculation(self):
        """Test PPDA calculation."""
        service = TacticalEventsService()
        
        events = [
            # Home team passes
            MatchEvent("e1", EventType.PASS, "home", "p1", 10.0, 60.0, 30.0),
            MatchEvent("e2", EventType.PASS, "home", "p1", 15.0, 65.0, 32.0),
            MatchEvent("e3", EventType.PASS, "home", "p1", 20.0, 70.0, 34.0),
            # Away defensive actions
            MatchEvent("e4", EventType.TACKLE, "away", "p2", 25.0, 72.0, 33.0),
        ]
        
        ppda = service.calculate_ppda(events, "away", "home")
        
        assert ppda.team_id == "away"
        assert ppda.passes_allowed == 3
        assert ppda.defensive_actions == 1
        assert ppda.ppda == pytest.approx(3.0)
    
    def test_pressure_zones(self):
        """Test pressing metrics by pitch zones."""
        service = TacticalEventsService(pitch_length=105.0)
        
        events = [
            # Defensive third (0-35m)
            MatchEvent("e1", EventType.PRESSURE, "home", "p1", 10.0, 20.0, 30.0),
            # Middle third (35-70m)
            MatchEvent("e2", EventType.PRESSURE, "home", "p2", 15.0, 50.0, 35.0),
            # Attacking third (70-105m)
            MatchEvent("e3", EventType.PRESSURE, "home", "p3", 20.0, 90.0, 40.0),
        ]
        
        metrics = service.calculate_pressure_metrics(events, "home")
        
        assert metrics.team_id == "home"
        assert metrics.defensive_third_presses == 1
        assert metrics.middle_third_presses == 1
        assert metrics.attacking_third_presses == 1
        assert metrics.total_presses == 3
    
    def test_ppda_no_defensive_actions(self):
        """Test PPDA when no defensive actions (infinity)."""
        service = TacticalEventsService()
        
        events = [
            MatchEvent("e1", EventType.PASS, "home", "p1", 10.0, 60.0, 30.0),
        ]
        
        ppda = service.calculate_ppda(events, "away", "home")
        
        assert ppda.ppda == float('inf')
