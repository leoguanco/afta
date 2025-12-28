"""
Vision Tasks (Celery Workers).

Background tasks for video processing, routed to the GPU worker queue.
"""

import logging
from typing import List
import cv2
import pandas as pd

from src.infrastructure.worker.celery_app import celery_app
from src.infrastructure.vision.yolo_detector import YOLODetector
from src.infrastructure.vision.byte_tracker import ByteTrackerAdapter
from src.infrastructure.storage.minio_adapter import MinIOAdapter
from src.domain.value_objects.trajectory import Trajectory

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, queue="gpu_queue", max_retries=2)
def process_video_task(self, video_path: str, output_path: str) -> dict:
    """
    Background task to process a video for object tracking.

    Args:
        video_path: Path to the input video file.
        output_path: Path to save the trajectory parquet file.

    Returns:
        Dict with status and trajectory count.
    """
    try:
        logger.info(f"Starting video processing: {video_path}")

        # Initialize detector and tracker
        detector = YOLODetector(confidence_threshold=0.5)
        tracker = ByteTrackerAdapter()

        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"status": "error", "message": f"Cannot open video: {video_path}"}

        all_trajectories: List[Trajectory] = []
        frame_id = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detect objects
            detections = detector.detect(frame)

            # Track objects
            trajectories = tracker.update(detections, frame_id)
            all_trajectories.extend(trajectories)

            frame_id += 1

            if frame_id % 100 == 0:
                logger.info(f"Processed {frame_id} frames, {len(all_trajectories)} trajectories")

        cap.release()

        # Save trajectories to Parquet file in MinIO
        
        # Convert trajectories to DataFrame
        trajectory_data = [
            {
                "frame_id": traj.frame_id,
                "object_id": traj.object_id,
                "x": traj.x,
                "y": traj.y,
                "confidence": getattr(traj, 'confidence', 1.0)
            }
            for traj in all_trajectories
        ]
        df = pd.DataFrame(trajectory_data)
        
        # Save to MinIO
        storage = MinIOAdapter()
        match_id = video_path.split("/")[-1].split(".")[0]  # Extract match ID from filename
        storage.save_parquet(f"tracking/{match_id}.parquet", df)

        logger.info(f"Video processing complete: {frame_id} frames, {len(all_trajectories)} trajectories")

        return {
            "status": "success",
            "video_path": video_path,
            "frame_count": frame_id,
            "trajectory_count": len(all_trajectories),
        }

    except Exception as exc:
        logger.error(f"Video processing failed: {exc}")
        raise self.retry(exc=exc, countdown=5)
