"""
VideoProcessor - Application Layer

Use Case for starting video processing.
"""
from dataclasses import dataclass
from typing import Optional

from src.domain.ports.video_processing_port import VideoProcessingPort


@dataclass
class VideoJobResult:
    """Result of starting a video processing job."""
    job_id: str
    status: str
    message: Optional[str] = None


class VideoProcessor:
    """
    Use Case: Process video.
    
    Orchestrates the dispatch of video processing jobs via injected port.
    """
    
    def __init__(self, dispatcher: VideoProcessingPort):
        """
        Initialize with dispatcher.
        
        Args:
            dispatcher: Port implementation for job dispatch
        """
        self.dispatcher = dispatcher
        
    def execute(self, video_path: str, output_path: str) -> VideoJobResult:
        """
        Start processing a video.
        
        Args:
            video_path: Input video path
            output_path: Output trajectory path
            
        Returns:
            VideoJobResult with job ID
        """
        job_id = self.dispatcher.start_processing(video_path, output_path)
        
        return VideoJobResult(
            job_id=job_id,
            status="PENDING",
            message=f"Video processing job started for {video_path}"
        )
