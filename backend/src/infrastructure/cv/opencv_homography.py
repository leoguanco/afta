"""
OpenCV Homography Adapter.

Infrastructure adapter for computing homography using OpenCV.
"""

from typing import List
import numpy as np
import cv2

from src.domain.value_objects.keypoint import Keypoint
from src.domain.value_objects.homography_matrix import HomographyMatrix


class OpenCVHomographyAdapter:
    """
    Adapter for computing homography using OpenCV.

    Uses cv2.findHomography() for accurate perspective transformation.
    """

    def compute(self, keypoints: List[Keypoint]) -> HomographyMatrix:
        """
        Compute homography matrix from keypoints using OpenCV.

        Args:
            keypoints: List of at least 4 keypoint correspondences.

        Returns:
            HomographyMatrix computed via RANSAC.

        Raises:
            ValueError: If less than 4 keypoints provided.
        """
        if len(keypoints) < 4:
            raise ValueError("At least 4 keypoints required for homography")

        # Extract source (pixel) and destination (pitch) points
        src_pts = np.float32([[kp.pixel_x, kp.pixel_y] for kp in keypoints])
        dst_pts = np.float32([[kp.pitch_x, kp.pitch_y] for kp in keypoints])

        # Compute homography using RANSAC
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        if H is None:
            raise ValueError("Failed to compute homography")

        # Convert numpy array to tuple of tuples
        matrix = tuple(tuple(row) for row in H.tolist())

        return HomographyMatrix(matrix=matrix)

    def transform_points(
        self, points: List[tuple], homography: HomographyMatrix
    ) -> List[tuple]:
        """
        Transform multiple points using a homography.

        Args:
            points: List of (x, y) tuples in pixel space.
            homography: The homography matrix.

        Returns:
            List of transformed (x, y) tuples in pitch space.
        """
        if not points:
            return []

        H = np.array(homography.matrix)
        pts = np.float32(points).reshape(-1, 1, 2)
        transformed = cv2.perspectiveTransform(pts, H)

        return [(float(p[0][0]), float(p[0][1])) for p in transformed]
