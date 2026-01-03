"""
OpenCV Scene Detector Adapter - Infrastructure Layer

Implements scene detection using OpenCV frame differencing.
"""
import cv2
import numpy as np
from typing import List, Tuple
import logging

from src.domain.services.scene_detector import Scene, SceneDetectorConfig

logger = logging.getLogger(__name__)


class OpenCVSceneDetector:
    """
    Scene detector using OpenCV frame differencing.
    
    Detects scene cuts by comparing consecutive frames.
    """
    
    def __init__(self, config: SceneDetectorConfig = None):
        """Initialize with config."""
        self.config = config or SceneDetectorConfig()
    
    def detect_scenes(self, video_path: str) -> List[Scene]:
        """
        Detect scenes in a video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            List of detected scenes
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Cannot open video: {video_path}")
            return []
        
        # Calculate frame differences
        differences = []
        prev_frame = None
        frame_id = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to grayscale for comparison
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if prev_frame is not None:
                # Calculate absolute difference
                diff = cv2.absdiff(prev_frame, gray)
                diff_ratio = np.mean(diff) / 255.0  # Normalize to 0-1
                differences.append(diff_ratio)
            
            prev_frame = gray
            frame_id += 1
            
            # Log progress every 500 frames
            if frame_id % 500 == 0:
                logger.info(f"Scene detection: processed {frame_id} frames")
        
        cap.release()
        
        # Convert differences to scenes
        return self._diffs_to_scenes(differences, frame_id)
    
    def _diffs_to_scenes(
        self, 
        differences: List[float], 
        total_frames: int
    ) -> List[Scene]:
        """Convert frame differences to scene list."""
        from src.domain.services.scene_detector import SceneDetector
        
        detector = SceneDetector(self.config)
        return detector.detect_scenes_from_diffs(differences)
    
    def detect_scenes_fast(
        self, 
        video_path: str,
        sample_rate: int = 5
    ) -> List[Scene]:
        """
        Fast scene detection by sampling frames.
        
        Args:
            video_path: Path to video file
            sample_rate: Process every Nth frame (default: 5)
            
        Returns:
            List of detected scenes
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Cannot open video: {video_path}")
            return []
        
        differences = []
        prev_frame = None
        frame_id = 0
        sampled_frame_ids = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_id % sample_rate == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Resize for faster processing
                small = cv2.resize(gray, (160, 90))
                
                if prev_frame is not None:
                    diff = cv2.absdiff(prev_frame, small)
                    diff_ratio = np.mean(diff) / 255.0
                    differences.append(diff_ratio)
                    sampled_frame_ids.append(frame_id)
                
                prev_frame = small
            
            frame_id += 1
        
        cap.release()
        
        # Find cut points
        scenes = []
        current_start = 0
        
        for i, (diff, fid) in enumerate(zip(differences, sampled_frame_ids)):
            if diff >= self.config.difference_threshold:
                # Detected scene cut
                if fid - current_start >= self.config.min_scene_frames:
                    scenes.append(Scene(
                        start_frame=current_start,
                        end_frame=fid,
                        label=f"scene_{len(scenes) + 1}"
                    ))
                current_start = fid + 1
        
        # Add final scene
        if frame_id - current_start >= self.config.min_scene_frames:
            scenes.append(Scene(
                start_frame=current_start,
                end_frame=frame_id,
                label=f"scene_{len(scenes) + 1}"
            ))
        
        logger.info(f"Detected {len(scenes)} scenes in {frame_id} frames")
        return scenes
