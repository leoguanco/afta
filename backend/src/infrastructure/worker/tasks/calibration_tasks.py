"""
Calibration Tasks (Celery Workers).

Background tasks for pitch calibration, routed to the CPU worker queue.
"""

import logging
from typing import List, Dict, Any

from src.infrastructure.worker.celery_app import celery_app
from src.infrastructure.cv.opencv_homography import OpenCVHomographyAdapter
from src.domain.value_objects.keypoint import Keypoint

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, queue="default", max_retries=2)
def calibrate_video_task(
    self, video_id: str, keypoints_data: List[Dict[str, Any]]
) -> dict:
    """
    Background task to compute homography for a video.

    Args:
        video_id: ID of the video being calibrated.
        keypoints_data: List of keypoint dicts with pixel/pitch coords.

    Returns:
        Dict with status and homography matrix.
    """
    try:
        logger.info(f"Starting calibration for video {video_id}")

        # Convert dict data to Keypoint objects
        keypoints = [
            Keypoint(
                pixel_x=kp["pixel_x"],
                pixel_y=kp["pixel_y"],
                pitch_x=kp["pitch_x"],
                pitch_y=kp["pitch_y"],
                name=kp.get("name"),
            )
            for kp in keypoints_data
        ]

        if len(keypoints) < 4:
            return {
                "status": "MANUAL_REQUIRED",
                "message": f"Need at least 4 keypoints, got {len(keypoints)}",
            }

        # Compute homography using OpenCV
        adapter = OpenCVHomographyAdapter()
        homography = adapter.compute(keypoints)

        logger.info(f"Calibration complete for video {video_id}")

        return {
            "status": "success",
            "video_id": video_id,
            "homography_matrix": [list(row) for row in homography.matrix],
        }

    except Exception as exc:
        logger.error(f"Calibration failed: {exc}")
        raise self.retry(exc=exc, countdown=3)
