"""
Vision Tasks (Celery Workers).

Background tasks for video processing, routed to the GPU worker queue.
"""
import logging
from typing import List

import cv2
import pandas as pd
from minio.error import S3Error

from src.domain.events.tracking_completed import TrackingCompletedEvent
from src.domain.value_objects.trajectory import Trajectory
from src.domain.services.trajectory_smoother import TrajectorySmoother, TrajectoryPoint
from src.domain.services.track_cleaner import TrackCleaner, CleaningConfig
from src.infrastructure.storage.minio_adapter import MinIOAdapter
from src.infrastructure.vision.byte_tracker import ByteTrackerAdapter
from src.infrastructure.vision.yolo_detector import YOLODetector
from src.infrastructure.worker.celery_app import celery_app
from src.infrastructure.adapters.savgol_smoother import SavitzkyGolaySmoother

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, queue="gpu_queue", max_retries=2)
def process_video_task(
    self, 
    video_path: str, 
    output_path: str,
    mode: str = "full_match"
) -> dict:
    """
    Background task to process a video for object tracking.

    Args:
        video_path: Path to the input video file.
        output_path: Path to save the trajectory parquet file.
        mode: Processing mode - "full_match" or "highlights"

    Returns:
        Dict with status and trajectory count.
    """
    try:
        logger.info(f"Starting video processing: {video_path} (mode: {mode})")

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

        # =====================================================
        # STABILIZATION: Smooth and Clean Trajectories
        # =====================================================
        logger.info(f"Raw trajectories: {len(all_trajectories)}, unique IDs: {len(set(t.object_id for t in all_trajectories))}")
        
        # Convert Trajectory objects to TrajectoryPoint for processing
        trajectory_points = [
            TrajectoryPoint(
                frame_id=t.frame_id,
                object_id=t.object_id,
                x=t.x,
                y=t.y,
                timestamp=t.frame_id * 0.04,
                object_type=t.object_type.value,
                confidence=getattr(t, 'confidence', 1.0)
            )
            for t in all_trajectories
        ]
        
        # Step 1: Smooth trajectories to reduce noise
        smoother = TrajectorySmoother(
            smoother=SavitzkyGolaySmoother(poly_order=2),
            window_size=5
        )
        smoothed_points = smoother.smooth_trajectories(trajectory_points)
        logger.info(f"After smoothing: {len(smoothed_points)} points")
        
        # Step 2: Clean tracks (remove ghosts, merge fragments)
        cleaner = TrackCleaner(CleaningConfig(
            min_track_duration_frames=15,  # ~0.5s at 30fps
            merge_distance_threshold=2.0,  # meters
            merge_time_gap_frames=10
        ))
        cleaned_points = cleaner.clean_tracks(smoothed_points)
        logger.info(f"After cleaning: {len(cleaned_points)} points, unique IDs: {len(set(p.object_id for p in cleaned_points))}")
        
        # =====================================================

        # Convert cleaned trajectories to DataFrame
        trajectory_data = [
            {
                "frame_id": traj.frame_id,
                "player_id": traj.object_id,
                "x": traj.x,
                "y": traj.y,
                "object_type": traj.object_type,
                "confidence": traj.confidence,
                "timestamp": traj.timestamp
            }
            for traj in cleaned_points
        ]
        df = pd.DataFrame(trajectory_data)
        
        # Save to MinIO with explicit error handling
        try:
            storage = MinIOAdapter()
            match_id = video_path.split("/")[-1].split(".")[0]  # Extract match ID from filename
            trajectory_key = f"tracking/{match_id}.parquet"
            storage.save_parquet(trajectory_key, df)
            logger.info(f"Successfully uploaded trajectory data to MinIO: {trajectory_key}")
        except S3Error as s3_err:
            logger.error(f"MinIO S3 error during upload: {s3_err}")
            # Re-raise to trigger Celery retry mechanism
            raise
        except Exception as upload_err:
            logger.error(f"Unexpected error during MinIO upload: {upload_err}")
            raise

        logger.info(f"Video processing complete: {frame_id} frames, {len(all_trajectories)} trajectories")

        # Emit domain event for tracking completion
        tracking_event = TrackingCompletedEvent(
            aggregate_id=match_id,
            match_id=match_id,
            video_path=video_path,
            trajectory_path=trajectory_key,
            frames_processed=frame_id,
            players_detected=len(set(t.object_id for t in all_trajectories))
        )
        
        logger.info(f"Emitted TrackingCompletedEvent: {tracking_event.event_id}")
        
        # Chain to metrics calculation task - ONLY for full match mode
        # Highlights mode skips metrics (they would be meaningless for discontinuous clips)
        metrics_triggered = False
        if mode == "full_match":
            celery_app.send_task(
                'calculate_match_metrics',
                args=[match_id, trajectory_data, []],  # tracking_data, event_data (empty for now)
                countdown=2  # Small delay to ensure trajectory is saved
            )
            logger.info(f"Chained metrics calculation for match {match_id}")
            metrics_triggered = True
        else:
            logger.info(f"Skipping metrics for highlight mode (match_id: {match_id})")

        return {
            "status": "success",
            "video_path": video_path,
            "mode": mode,
            "frame_count": frame_id,
            "trajectory_count": len(all_trajectories),
            "event_id": tracking_event.event_id,
            "metrics_triggered": metrics_triggered
        }

    except S3Error as s3_exc:
        logger.error(f"MinIO connectivity issue, will retry: {s3_exc}")
        raise self.retry(exc=s3_exc, countdown=5)
    except Exception as exc:
        logger.error(f"Video processing failed: {exc}")
        raise self.retry(exc=exc, countdown=5)

