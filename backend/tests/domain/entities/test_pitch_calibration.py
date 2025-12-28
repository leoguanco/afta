"""
TDD Tests for PitchCalibration Entity.

Tests for rich domain logic in pitch calibration.
"""
import pytest
from src.domain.entities.pitch_calibration import PitchCalibration, CalibrationResult
from src.domain.value_objects.keypoint import Keypoint
from src.domain.value_objects.homography_matrix import HomographyMatrix


class TestPitchCalibration:
    """Test suite for PitchCalibration rich entity."""

    def test_requires_minimum_four_keypoints(self):
        """Homography calculation requires at least 4 keypoints."""
        # Given: Only 3 keypoints
        keypoints = [
            Keypoint(pixel_x=0, pixel_y=0, pitch_x=0, pitch_y=0),
            Keypoint(pixel_x=100, pixel_y=0, pitch_x=105, pitch_y=0),
            Keypoint(pixel_x=0, pixel_y=100, pitch_x=0, pitch_y=68),
        ]
        calibration = PitchCalibration(keypoints=keypoints)
        
        # When: Calculate homography
        result = calibration.calculate_homography()
        
        # Then: Should fail with INSUFFICIENT_KEYPOINTS
        assert result.success is False
        assert result.error == "INSUFFICIENT_KEYPOINTS"

    def test_calculates_homography_with_four_keypoints(self):
        """Should calculate homography with 4+ keypoints."""
        # Given: 4 corner keypoints (full pitch)
        keypoints = [
            Keypoint(pixel_x=0, pixel_y=0, pitch_x=0, pitch_y=0),
            Keypoint(pixel_x=1920, pixel_y=0, pitch_x=105, pitch_y=0),
            Keypoint(pixel_x=1920, pixel_y=1080, pitch_x=105, pitch_y=68),
            Keypoint(pixel_x=0, pixel_y=1080, pitch_x=0, pitch_y=68),
        ]
        calibration = PitchCalibration(keypoints=keypoints)
        
        # When: Calculate homography
        result = calibration.calculate_homography()
        
        # Then: Should succeed and return matrix
        assert result.success is True
        assert result.homography_matrix is not None
        assert isinstance(result.homography_matrix, HomographyMatrix)

    def test_homography_matrix_is_cached(self):
        """Calculated homography should be cached."""
        keypoints = [
            Keypoint(pixel_x=0, pixel_y=0, pitch_x=0, pitch_y=0),
            Keypoint(pixel_x=1920, pixel_y=0, pitch_x=105, pitch_y=0),
            Keypoint(pixel_x=1920, pixel_y=1080, pitch_x=105, pitch_y=68),
            Keypoint(pixel_x=0, pixel_y=1080, pitch_x=0, pitch_y=68),
        ]
        calibration = PitchCalibration(keypoints=keypoints)
        
        # Calculate once
        calibration.calculate_homography()
        
        # Get cached
        cached = calibration.get_homography()
        
        assert cached is not None

    def test_adding_keypoint_invalidates_cache(self):
        """Adding a keypoint should invalidate the cached homography."""
        keypoints = [
            Keypoint(pixel_x=0, pixel_y=0, pitch_x=0, pitch_y=0),
            Keypoint(pixel_x=1920, pixel_y=0, pitch_x=105, pitch_y=0),
            Keypoint(pixel_x=1920, pixel_y=1080, pitch_x=105, pitch_y=68),
            Keypoint(pixel_x=0, pixel_y=1080, pitch_x=0, pitch_y=68),
        ]
        calibration = PitchCalibration(keypoints=keypoints)
        
        # Calculate and cache
        calibration.calculate_homography()
        assert calibration.get_homography() is not None
        
        # Add new keypoint
        calibration.add_keypoint(
            Keypoint(pixel_x=960, pixel_y=540, pitch_x=52.5, pitch_y=34)
        )
        
        # Cache should be invalidated
        assert calibration.get_homography() is None

    def test_calibration_result_dataclass(self):
        """CalibrationResult should have proper fields."""
        # Success case
        success_result = CalibrationResult(
            success=True,
            homography_matrix=HomographyMatrix(matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        )
        assert success_result.success is True
        assert success_result.error is None
        
        # Failure case
        failure_result = CalibrationResult(
            success=False,
            error="SOME_ERROR"
        )
        assert failure_result.success is False
        assert failure_result.homography_matrix is None
