"""
TDD Tests for Savitzky-Golay Filter in PlayerTrajectory.

Tests for smooth velocity calculation using scipy's savgol_filter.
"""
import pytest
import numpy as np
from src.domain.entities.player_trajectory import PlayerTrajectory, FramePosition


class TestSavitzkyGolayFilter:
    """Test suite for Savitzky-Golay velocity smoothing."""

    def test_smooth_velocity_removes_noise(self):
        """Savitzky-Golay should smooth noisy velocity data."""
        # Given: A trajectory with noisy position data
        positions = []
        for i in range(25):  # 1 second at 25fps
            # Linear motion with noise
            x = i * 0.4 + np.random.normal(0, 0.05)  # ~10 m/s with noise
            y = 34.0  # Constant y
            positions.append(FramePosition(
                frame=i,
                timestamp=i / 25.0,
                x=x,
                y=y
            ))
        
        trajectory = PlayerTrajectory(
            player_id="player_1",
            team_id="home",
            positions=positions
        )
        
        # When: Calculate physical metrics with Savitzky-Golay
        metrics = trajectory.calculate_physical_metrics(fps=25)
        
        # Then: Velocities should be smooth (low variance)
        assert len(metrics.frame_velocities) > 0
        velocities = list(metrics.frame_velocities.values())
        velocity_std = np.std(velocities)
        
        # Smoothed data should have lower variance than raw noise
        assert velocity_std < 5.0  # Reasonable smoothness

    def test_savgol_preserves_signal_shape(self):
        """Savitzky-Golay should preserve acceleration patterns."""
        # Given: A trajectory with clear acceleration phase
        positions = []
        for i in range(50):  # 2 seconds
            t = i / 25.0
            # Accelerating motion: x = 0.5 * a * t^2, a = 5 m/s^2
            x = 0.5 * 5.0 * (t ** 2)
            y = 34.0
            positions.append(FramePosition(
                frame=i,
                timestamp=t,
                x=x,
                y=y
            ))
        
        trajectory = PlayerTrajectory(
            player_id="player_1",
            team_id="home",
            positions=positions
        )
        
        # When: Calculate metrics
        metrics = trajectory.calculate_physical_metrics(fps=25)
        
        # Then: Velocity should increase over time (acceleration detected)
        velocities = list(metrics.frame_velocities.values())
        early_velocity = np.mean(velocities[:10])
        late_velocity = np.mean(velocities[-10:])
        
        assert late_velocity > early_velocity  # Acceleration preserved

    def test_sprint_detection_with_savgol(self):
        """Sprint detection should work with smoothed velocity."""
        # Given: A trajectory with a sprint (>25 km/h = ~7 m/s)
        positions = []
        for i in range(75):  # 3 seconds
            t = i / 25.0
            if t < 1.0:
                x = t * 5.0  # Slow start (5 m/s)
            elif t < 2.0:
                x = 5.0 + (t - 1.0) * 8.0  # Sprint phase (8 m/s = 28.8 km/h)
            else:
                x = 13.0 + (t - 2.0) * 4.0  # Decelerate
            positions.append(FramePosition(
                frame=i,
                timestamp=t,
                x=x,
                y=34.0
            ))
        
        trajectory = PlayerTrajectory(
            player_id="player_1",
            team_id="home",
            positions=positions
        )
        
        # When: Calculate metrics
        metrics = trajectory.calculate_physical_metrics(fps=25)
        
        # Then: Should detect at least one sprint
        assert metrics.sprint_count >= 1
        assert metrics.max_speed >= 25.0  # At least 25 km/h detected

    def test_short_trajectory_uses_fallback(self):
        """Very short trajectories should fallback to simple smoothing."""
        # Given: A trajectory with only 3 positions (too short for savgol)
        positions = [
            FramePosition(frame=0, timestamp=0.0, x=0.0, y=0.0),
            FramePosition(frame=1, timestamp=0.04, x=0.4, y=0.0),
            FramePosition(frame=2, timestamp=0.08, x=0.8, y=0.0),
        ]
        
        trajectory = PlayerTrajectory(
            player_id="player_1",
            team_id="home",
            positions=positions
        )
        
        # When: Calculate metrics (should not crash)
        metrics = trajectory.calculate_physical_metrics(fps=25)
        
        # Then: Should still compute reasonable values
        assert metrics.total_distance >= 0
        assert metrics.avg_speed >= 0
