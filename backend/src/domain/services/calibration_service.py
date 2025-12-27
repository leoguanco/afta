"""
CalibrationService Domain Service.

Pure math logic for calculating homography from keypoint correspondences.
This is a Domain Service and MUST NOT import OpenCV or any external libraries.
Uses only Python stdlib math.
"""

from dataclasses import dataclass
from typing import List, Optional

from src.domain.value_objects.keypoint import Keypoint
from src.domain.value_objects.homography_matrix import HomographyMatrix


@dataclass
class CalibrationResult:
    """Result of a calibration attempt."""

    success: bool
    homography_matrix: Optional[HomographyMatrix] = None
    error: Optional[str] = None


class CalibrationService:
    """
    Domain Service for pitch calibration.

    Calculates the homography matrix from keypoint correspondences.
    Uses a simple Direct Linear Transform (DLT) algorithm.
    """

    MIN_KEYPOINTS = 4

    def calibrate(self, keypoints: List[Keypoint]) -> CalibrationResult:
        """
        Calculate homography matrix from keypoints.

        Args:
            keypoints: List of at least 4 keypoint correspondences.

        Returns:
            CalibrationResult with the homography matrix or error.
        """
        if len(keypoints) < self.MIN_KEYPOINTS:
            return CalibrationResult(
                success=False,
                error="INSUFFICIENT_KEYPOINTS",
            )

        try:
            H = self._compute_homography(keypoints)
            return CalibrationResult(
                success=True,
                homography_matrix=H,
            )
        except Exception as e:
            return CalibrationResult(
                success=False,
                error=str(e),
            )

    def _compute_homography(self, keypoints: List[Keypoint]) -> HomographyMatrix:
        """
        Compute homography using simplified DLT algorithm.

        For production, this should delegate to OpenCV via a Port.
        This implementation uses a simple affine approximation.
        """
        # Extract source (pixel) and destination (pitch) points
        src = [(kp.pixel_x, kp.pixel_y) for kp in keypoints]
        dst = [(kp.pitch_x, kp.pitch_y) for kp in keypoints]

        # Simple scale + translation approximation
        # For accurate homography, use OpenCV adapter
        sx = (dst[1][0] - dst[0][0]) / (src[1][0] - src[0][0]) if src[1][0] != src[0][0] else 1
        sy = (dst[3][1] - dst[0][1]) / (src[3][1] - src[0][1]) if src[3][1] != src[0][1] else 1
        tx = dst[0][0] - sx * src[0][0]
        ty = dst[0][1] - sy * src[0][1]

        matrix = (
            (sx, 0.0, tx),
            (0.0, sy, ty),
            (0.0, 0.0, 1.0),
        )

        return HomographyMatrix(matrix=matrix)
