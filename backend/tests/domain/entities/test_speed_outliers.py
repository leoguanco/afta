"""
TDD Tests for Speed Outlier Detection.

Tests for the flag_outliers() and clip_outliers() methods.
"""
import pytest
from src.domain.entities.player_trajectory import PlayerTrajectory, TrajectoryFrame


class TestSpeedOutlierDetection:
    """Test suite for speed outlier detection per spec."""

    def test_flag_outliers_identifies_unrealistic_speeds(self):
        """Should flag frames with speed > 36 km/h."""
        # Given: A trajectory with one frame having unrealistic speed
        # At 25 fps, 36 km/h = 10 m/s = 0.4m per frame
        # Creating a 2m jump (50 m/s = 180 km/h) which is impossible
        frames = [
            TrajectoryFrame(frame_id=0, x=0.0, y=0.0, timestamp=0.0),
            TrajectoryFrame(frame_id=1, x=0.3, y=0.0, timestamp=0.04),  # Normal: 7.5 m/s
            TrajectoryFrame(frame_id=2, x=2.3, y=0.0, timestamp=0.08),  # Outlier: 50 m/s
            TrajectoryFrame(frame_id=3, x=2.5, y=0.0, timestamp=0.12),  # Normal: 5 m/s
        ]
        trajectory = PlayerTrajectory(player_id="P1", frames=frames, fps=25.0)
        
        # When: Flag outliers
        outliers = trajectory.flag_outliers(max_speed_kmh=36.0)
        
        # Then: Should find frame 2 as outlier
        assert 2 in outliers
        assert 1 not in outliers
        assert 3 not in outliers

    def test_flag_outliers_returns_empty_for_valid_trajectory(self):
        """Should return empty list for valid speeds."""
        # Given: Normal walking/jogging trajectory
        frames = [
            TrajectoryFrame(frame_id=i, x=i * 0.2, y=0.0, timestamp=i * 0.04)
            for i in range(10)
        ]
        trajectory = PlayerTrajectory(player_id="P1", frames=frames, fps=25.0)
        
        # When: Flag outliers
        outliers = trajectory.flag_outliers(max_speed_kmh=36.0)
        
        # Then: No outliers
        assert len(outliers) == 0

    def test_flag_outliers_custom_threshold(self):
        """Should respect custom threshold."""
        # Given: Trajectory at ~30 km/h (normal sprint)
        # 30 km/h = 8.33 m/s = 0.333m per frame at 25fps
        frames = [
            TrajectoryFrame(frame_id=i, x=i * 0.35, y=0.0, timestamp=i * 0.04)
            for i in range(5)
        ]
        trajectory = PlayerTrajectory(player_id="P1", frames=frames, fps=25.0)
        
        # When: Flag with lower threshold
        outliers_low = trajectory.flag_outliers(max_speed_kmh=25.0)
        outliers_high = trajectory.flag_outliers(max_speed_kmh=36.0)
        
        # Then: Lower threshold flags, higher doesn't
        assert len(outliers_low) > 0
        assert len(outliers_high) == 0

    def test_usain_bolt_speed_flagged(self):
        """Speeds above human maximum should be flagged."""
        # Usain Bolt max: ~44 km/h. At 25 fps = 0.49m per frame
        # Let's test 50 km/h = 0.56m per frame
        frames = [
            TrajectoryFrame(frame_id=0, x=0.0, y=0.0, timestamp=0.0),
            TrajectoryFrame(frame_id=1, x=0.6, y=0.0, timestamp=0.04),  # 54 km/h
        ]
        trajectory = PlayerTrajectory(player_id="P1", frames=frames, fps=25.0)
        
        # When: Flag outliers at 36 km/h (sports threshold)
        outliers = trajectory.flag_outliers(max_speed_kmh=36.0)
        
        # Then: Should flag
        assert 1 in outliers
