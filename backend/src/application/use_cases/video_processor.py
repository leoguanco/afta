"""
VideoProcessor - Application Layer

Use Case for starting video processing.
"""
import os
from dataclasses import dataclass
from typing import Optional

from src.domain.ports.video_processing_port import VideoProcessingPort
from src.domain.ports.match_repository import MatchRepository
from src.domain.entities.match import Match


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
    Ensures a parent Match entity exists for the video.
    """
    
    def __init__(self, dispatcher: VideoProcessingPort, match_repo: MatchRepository):
        """
        Initialize with dispatcher and repository.
        
        Args:
            dispatcher: Port implementation for job dispatch
            match_repo: Port implementation for match persistence
        """
        self.dispatcher = dispatcher
        self.match_repo = match_repo
        
    def execute(self, video_path: str, output_path: str) -> VideoJobResult:
        """
        Start processing a video.
        
        Automatically creates a Match record if one doesn't exist for this video,
        preventing ForeignKey errors during metrics saving.
        
        Args:
            video_path: Input video path
            output_path: Output trajectory path
            
        Returns:
            VideoJobResult with job ID
        """
        # 1. Derive match_id from filename (e.g., "/app/data/2-boca.mp4" -> "2-boca")
        filename = os.path.basename(video_path)
        match_id = os.path.splitext(filename)[0]
        
        # 2. Ensure Match record exists
        # We try to fetch it first. If missing, we create a placeholder.
        # This is critical for custom video uploads where no StatsBomb data exists.
        existing_match = self.match_repo.get_match(match_id)
        
        if not existing_match:
            # Create placeholder match
            # We don't know teams, so we use generic placeholders.
            new_match = Match(
                match_id=match_id,
                home_team_id="Home",
                away_team_id="Away",
                competition="Custom Upload",
                season="N/A",
                match_date=None
            )
            # Persist it
            self.match_repo.save(new_match)
            # Note: We rely on the repo implementation to handle specific DB fields.
        
        # 3. Dispatch Job
        job_id = self.dispatcher.start_processing(video_path, output_path)
        
        return VideoJobResult(
            job_id=job_id,
            status="PENDING",
            message=f"Video processing job started for {match_id} (Match Record ensured)"
        )
