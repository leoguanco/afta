"""
PitchCalibration Entity - Domain Layer

Rich entity representing a pitch calibration with homography calculation.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple

from src.domain.value_objects.keypoint import Keypoint
from src.domain.value_objects.homography_matrix import HomographyMatrix


@dataclass
class CalibrationResult:
    """Value object for calibration result."""
    success: bool
    homography_matrix: Optional[HomographyMatrix] = None
    error: Optional[str] = None


class PitchCalibration:
    """
    Rich domain entity representing pitch calibration.
    
    Encapsulates keypoint correspondences and provides methods to
    calculate the homography transformation.
    """
    
    MIN_KEYPOINTS = 4
    
    def __init__(self, keypoints: List[Keypoint]):
        """
        Initialize pitch calibration.
        
        Args:
            keypoints: List of keypoint correspondences (pixel <-> pitch)
        """
        self.keypoints = keypoints
        self._homography: Optional[HomographyMatrix] = None
    
    def calculate_homography(self) -> CalibrationResult:
        """
        Calculate homography matrix from keypoints using DLT.
        
        Returns:
            CalibrationResult with matrix or error
        """
        if len(self.keypoints) < self.MIN_KEYPOINTS:
            return CalibrationResult(
                success=False,
                error="INSUFFICIENT_KEYPOINTS"
            )
        
        try:
            matrix = self._compute_homography()
            self._homography = matrix
            return CalibrationResult(
                success=True,
                homography_matrix=matrix
            )
        except Exception as e:
            return CalibrationResult(
                success=False,
                error=str(e)
            )
    
    def get_homography(self) -> Optional[HomographyMatrix]:
        """Get the calculated homography (if available)."""
        return self._homography
    
    def add_keypoint(self, keypoint: Keypoint) -> None:
        """Add a new keypoint correspondence."""
        self.keypoints.append(keypoint)
        self._homography = None  # Invalidate cache
    
    def _compute_homography(self) -> HomographyMatrix:
        """
        Compute homography using simplified DLT algorithm.
        
        For production, this should delegate to OpenCV via a Port.
        This implementation uses a simple affine approximation.
        """
        src = [(kp.pixel_x, kp.pixel_y) for kp in self.keypoints]
        dst = [(kp.pitch_x, kp.pitch_y) for kp in self.keypoints]
        
        # Simple scale + translation approximation
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
    
    def __repr__(self) -> str:
        return f"PitchCalibration(keypoints={len(self.keypoints)})"
