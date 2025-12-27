"""
YOLO Detector Adapter.

Infrastructure adapter implementing ObjectDetector using YOLOv8.
"""

from typing import List, Optional
import numpy as np

from src.domain.ports.object_detector import ObjectDetector
from src.domain.value_objects.bounding_box import BoundingBox


class YOLODetector(ObjectDetector):
    """
    Adapter for YOLOv8 object detection.

    Wraps ultralytics YOLO model behind the ObjectDetector port.
    """

    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5):
        """
        Initialize the YOLO detector.

        Args:
            model_path: Path to YOLO weights (default: yolov8n.pt).
            confidence_threshold: Minimum confidence for detections.
        """
        self.model_path = model_path or "yolov8n.pt"
        self.confidence_threshold = confidence_threshold
        self.model = None

    def load_model(self, model_path: str) -> None:
        """
        Load the YOLO model.

        Args:
            model_path: Path to the model weights.
        """
        from ultralytics import YOLO

        self.model_path = model_path
        self.model = YOLO(self.model_path)

    def detect(self, frame: np.ndarray) -> List[BoundingBox]:
        """
        Detect objects in a single frame.

        Args:
            frame: Image frame as numpy array (H, W, C).

        Returns:
            List of detected bounding boxes.
        """
        if self.model is None:
            self.load_model(self.model_path)

        # Run inference
        results = self.model(frame, verbose=False)[0]

        bounding_boxes = []
        for box in results.boxes:
            confidence = float(box.conf[0])
            if confidence < self.confidence_threshold:
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            class_id = int(box.cls[0])

            bounding_boxes.append(
                BoundingBox(
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    confidence=confidence,
                    class_id=class_id,
                )
            )

        return bounding_boxes
