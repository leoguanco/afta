"""
VideoProcessingPort - Domain Layer

Port for dispatching video processing jobs.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class VideoProcessingPort(ABC):
    """
    Abstract interface for video processing operations.
    """
    
    @abstractmethod
    def start_processing(self, video_path: str, output_path: str) -> str:
        """
        Start an asynchronous video processing job.
        
        Args:
            video_path: Path to input video
            output_path: Path to output trajectory file
            
        Returns:
            Job ID of the started process
        """
        ...
