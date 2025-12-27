"""
TDD Tests for Keypoint Value Object.

Tests the keypoint data structure for pitch landmarks.
"""

import pytest
from src.domain.value_objects.keypoint import Keypoint


class TestKeypoint:
    """Test Keypoint value object."""

    def test_create_keypoint(self):
        """Should create a Keypoint with all required fields."""
        kp = Keypoint(
            pixel_x=500.0,
            pixel_y=300.0,
            pitch_x=0.0,
            pitch_y=0.0,
            name="corner_left_top",
        )
        assert kp.pixel_x == 500.0
        assert kp.pixel_y == 300.0
        assert kp.pitch_x == 0.0
        assert kp.pitch_y == 0.0
        assert kp.name == "corner_left_top"

    def test_keypoint_center_circle(self):
        """Center circle keypoint should map correctly."""
        kp = Keypoint(
            pixel_x=640.0,
            pixel_y=360.0,
            pitch_x=52.5,
            pitch_y=34.0,
            name="center_spot",
        )
        assert kp.pitch_x == 52.5
        assert kp.pitch_y == 34.0

    def test_keypoint_is_immutable(self):
        """Keypoint should be immutable (frozen dataclass)."""
        kp = Keypoint(
            pixel_x=500.0,
            pixel_y=300.0,
            pitch_x=0.0,
            pitch_y=0.0,
        )
        with pytest.raises(AttributeError):
            kp.pixel_x = 600.0

    def test_keypoint_as_pixel_tuple(self):
        """Should return pixel coordinates as tuple."""
        kp = Keypoint(pixel_x=500.0, pixel_y=300.0, pitch_x=0.0, pitch_y=0.0)
        assert kp.pixel_coords == (500.0, 300.0)

    def test_keypoint_as_pitch_tuple(self):
        """Should return pitch coordinates as tuple."""
        kp = Keypoint(pixel_x=500.0, pixel_y=300.0, pitch_x=52.5, pitch_y=34.0)
        assert kp.pitch_coords == (52.5, 34.0)
