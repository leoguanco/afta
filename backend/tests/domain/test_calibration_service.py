"""
TDD Tests for CalibrationService Domain Service.

Tests the pure math logic for homography calculation.
"""

import pytest
from src.domain.services.calibration_service import CalibrationService, CalibrationResult
from src.domain.value_objects.keypoint import Keypoint


class TestCalibrationService:
    """Test CalibrationService domain service."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return CalibrationService()

    @pytest.fixture
    def four_keypoints(self):
        """Four corner keypoints for a simple mapping."""
        return [
            Keypoint(pixel_x=0, pixel_y=0, pitch_x=0, pitch_y=0, name="corner_tl"),
            Keypoint(pixel_x=1280, pixel_y=0, pitch_x=105, pitch_y=0, name="corner_tr"),
            Keypoint(pixel_x=1280, pixel_y=720, pitch_x=105, pitch_y=68, name="corner_br"),
            Keypoint(pixel_x=0, pixel_y=720, pitch_x=0, pitch_y=68, name="corner_bl"),
        ]

    def test_calibrate_with_four_points(self, service, four_keypoints):
        """Should calculate homography with 4 keypoints."""
        result = service.calibrate(four_keypoints)
        assert result.success is True
        assert result.homography_matrix is not None

    def test_calibrate_fails_with_less_than_four_points(self, service):
        """Should fail if less than 4 keypoints provided."""
        keypoints = [
            Keypoint(pixel_x=0, pixel_y=0, pitch_x=0, pitch_y=0),
            Keypoint(pixel_x=100, pixel_y=0, pitch_x=10, pitch_y=0),
        ]
        result = service.calibrate(keypoints)
        assert result.success is False
        assert result.error == "INSUFFICIENT_KEYPOINTS"

    def test_calibrate_transforms_points_correctly(self, service, four_keypoints):
        """Transformed points should be close to expected pitch coordinates."""
        result = service.calibrate(four_keypoints)
        # Center of video (640, 360) should map to center of pitch (52.5, 34)
        H = result.homography_matrix
        tx, ty = H.transform_point(640, 360)
        assert tx == pytest.approx(52.5, abs=1.0)
        assert ty == pytest.approx(34.0, abs=1.0)
