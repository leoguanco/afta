"""
ByteTrack Adapter.

Infrastructure adapter implementing ObjectTracker using ByteTrack algorithm.
Note: This is a simplified implementation. For production, use the full ByteTrack library.
"""

from typing import List, Dict
import numpy as np

from src.domain.ports.object_tracker import ObjectTracker
from src.domain.value_objects.bounding_box import BoundingBox
from src.domain.value_objects.trajectory import Trajectory, ObjectType


# Mapping from YOLO class IDs to ObjectType
CLASS_ID_MAP = {
    0: ObjectType.PLAYER,      # person
    32: ObjectType.BALL,       # sports ball
    # Add more mappings as needed
}


class ByteTrackerAdapter(ObjectTracker):
    """
    Simplified tracker adapter.

    For production use, integrate the full ByteTrack library.
    This implementation uses a simple IoU-based tracking approach.
    """

    def __init__(self, iou_threshold: float = 0.5, max_age: int = 30):
        """
        Initialize the tracker.

        Args:
            iou_threshold: Minimum IoU for matching detections to tracks.
            max_age: Maximum frames to keep a track without detection.
        """
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.tracks: Dict[int, dict] = {}
        self.next_id = 1

    def reset(self) -> None:
        """Reset the tracker state for a new video."""
        self.tracks = {}
        self.next_id = 1

    def update(self, detections: List[BoundingBox], frame_id: int) -> List[Trajectory]:
        """
        Update tracker with new detections.

        Args:
            detections: List of bounding boxes from detector.
            frame_id: Current frame number.

        Returns:
            List of trajectories with assigned IDs.
        """
        trajectories = []

        # Match detections to existing tracks
        matched_detections = set()
        for track_id, track in list(self.tracks.items()):
            best_iou = 0
            best_det_idx = -1

            for i, det in enumerate(detections):
                if i in matched_detections:
                    continue

                iou = self._calculate_iou(track["bbox"], det)
                if iou > best_iou and iou > self.iou_threshold:
                    best_iou = iou
                    best_det_idx = i

            if best_det_idx >= 0:
                # Update track
                det = detections[best_det_idx]
                track["bbox"] = det
                track["age"] = 0
                matched_detections.add(best_det_idx)

                # Create trajectory
                cx, cy = det.center
                obj_type = CLASS_ID_MAP.get(det.class_id, ObjectType.PLAYER)
                trajectories.append(
                    Trajectory(
                        frame_id=frame_id,
                        object_id=track_id,
                        x=cx,
                        y=cy,
                        object_type=obj_type,
                        confidence=det.confidence,
                    )
                )
            else:
                # Age the track
                track["age"] += 1
                if track["age"] > self.max_age:
                    del self.tracks[track_id]

        # Create new tracks for unmatched detections
        for i, det in enumerate(detections):
            if i not in matched_detections:
                track_id = self.next_id
                self.next_id += 1
                self.tracks[track_id] = {"bbox": det, "age": 0}

                cx, cy = det.center
                obj_type = CLASS_ID_MAP.get(det.class_id, ObjectType.PLAYER)
                trajectories.append(
                    Trajectory(
                        frame_id=frame_id,
                        object_id=track_id,
                        x=cx,
                        y=cy,
                        object_type=obj_type,
                        confidence=det.confidence,
                    )
                )

        return trajectories

    def _calculate_iou(self, box1: BoundingBox, box2: BoundingBox) -> float:
        """Calculate Intersection over Union between two boxes."""
        x1 = max(box1.x1, box2.x1)
        y1 = max(box1.y1, box2.y1)
        x2 = min(box1.x2, box2.x2)
        y2 = min(box1.y2, box2.y2)

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = box1.width * box1.height
        area2 = box2.width * box2.height
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0
