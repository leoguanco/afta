"""
Scene Detector - Domain Service

Detects scene cuts/transitions in video using frame differencing.
Used for Highlight Mode processing.
"""
from dataclasses import dataclass
from typing import List, Protocol
from abc import abstractmethod


@dataclass
class Scene:
    """Represents a detected scene in a video."""
    start_frame: int
    end_frame: int
    label: str = "unknown"
    
    @property
    def duration_frames(self) -> int:
        return self.end_frame - self.start_frame


class FrameAnalyzerPort(Protocol):
    """Port for frame analysis operations."""
    
    @abstractmethod
    def calculate_frame_difference(self, frame1, frame2) -> float:
        """Calculate difference between two frames (0-1)."""
        ...


@dataclass
class SceneDetectorConfig:
    """Configuration for scene detection."""
    difference_threshold: float = 0.30  # 30% change = scene cut
    min_scene_frames: int = 30  # Minimum frames for valid scene (~1s at 30fps)


class SceneDetector:
    """
    Domain service for detecting scene cuts in video.
    
    Uses frame differencing to identify transitions.
    """
    
    def __init__(self, config: SceneDetectorConfig = None):
        """Initialize detector."""
        self.config = config or SceneDetectorConfig()
    
    def detect_scenes_from_diffs(
        self, 
        frame_differences: List[float]
    ) -> List[Scene]:
        """
        Detect scenes from pre-computed frame differences.
        
        Args:
            frame_differences: List of frame-to-frame difference values (0-1)
            
        Returns:
            List of detected scenes
        """
        if not frame_differences:
            return []
        
        scenes = []
        current_start = 0
        
        for i, diff in enumerate(frame_differences):
            if diff >= self.config.difference_threshold:
                # Scene cut detected
                if i - current_start >= self.config.min_scene_frames:
                    scenes.append(Scene(
                        start_frame=current_start,
                        end_frame=i,
                        label=f"scene_{len(scenes) + 1}"
                    ))
                current_start = i + 1
        
        # Add final scene
        total_frames = len(frame_differences) + 1
        if total_frames - current_start >= self.config.min_scene_frames:
            scenes.append(Scene(
                start_frame=current_start,
                end_frame=total_frames,
                label=f"scene_{len(scenes) + 1}"
            ))
        
        return scenes
