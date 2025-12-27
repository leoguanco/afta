"""
TDD Tests for Trajectory Value Object.

Tests the trajectory data structure for tracking results.
"""

import pytest
from src.domain.value_objects.trajectory import Trajectory, ObjectType


class TestObjectType:
    """Test ObjectType enum."""

    def test_player_type(self):
        """ObjectType should have PLAYER variant."""
        assert ObjectType.PLAYER.value == "player"

    def test_ball_type(self):
        """ObjectType should have BALL variant."""
        assert ObjectType.BALL.value == "ball"

    def test_referee_type(self):
        """ObjectType should have REFEREE variant."""
        assert ObjectType.REFEREE.value == "referee"


class TestTrajectory:
    """Test Trajectory value object."""

    def test_create_trajectory(self):
        """Should create a Trajectory with all required fields."""
        traj = Trajectory(
            frame_id=100,
            object_id=5,
            x=52.5,
            y=34.0,
            object_type=ObjectType.PLAYER,
        )
        assert traj.frame_id == 100
        assert traj.object_id == 5
        assert traj.x == 52.5
        assert traj.y == 34.0
        assert traj.object_type == ObjectType.PLAYER

    def test_trajectory_is_immutable(self):
        """Trajectory should be immutable (frozen dataclass)."""
        traj = Trajectory(
            frame_id=100,
            object_id=5,
            x=52.5,
            y=34.0,
            object_type=ObjectType.PLAYER,
        )
        with pytest.raises(AttributeError):
            traj.x = 60.0

    def test_trajectory_with_confidence(self):
        """Trajectory can have optional confidence score."""
        traj = Trajectory(
            frame_id=100,
            object_id=5,
            x=52.5,
            y=34.0,
            object_type=ObjectType.PLAYER,
            confidence=0.95,
        )
        assert traj.confidence == 0.95
