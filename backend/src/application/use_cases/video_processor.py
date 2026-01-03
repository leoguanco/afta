"""
VideoProcessor - Application Layer

Use Case for starting video processing.
"""
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any

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
        
    def execute(
        self, 
        video_path: str, 
        output_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        sync_offset_seconds: float = 0.0,
        mode: str = "full_match"
    ) -> VideoJobResult:
        """
        Start processing a video.
        
        Automatically creates a Match record if one doesn't exist for this video,
        using provided metadata if available.
        
        Args:
            video_path: Input video path
            output_path: Output trajectory path
            metadata: Optional dict with home_team, away_team, date, competition
            sync_offset_seconds: Time offset for syncing video with event data
            mode: Processing mode - "full_match" or "highlights"
            
        Returns:
            VideoJobResult with job ID
        """
        # 1. Derive match_id from filename (e.g., "/app/data/2-boca.mp4" -> "2-boca")
        filename = os.path.basename(video_path)
        match_id = os.path.splitext(filename)[0]
        
        # 2. Check if Match exists (e.g., from StatsBomb ingestion)
        existing_match = self.match_repo.get_match(match_id)
        
        if existing_match:
            # Match exists (e.g., from StatsBomb) - video will be linked to it
            # Don't overwrite existing metadata
            pass
        else:
            # Create new Match with provided metadata or placeholders
            home_team = metadata.get("home_team", "Home") if metadata else "Home"
            away_team = metadata.get("away_team", "Away") if metadata else "Away"
            competition = metadata.get("competition", "Custom Upload") if metadata else "Custom Upload"
            match_date = metadata.get("date") if metadata else None
            
            new_match = Match(
                match_id=match_id,
                home_team_id=home_team,
                away_team_id=away_team,
                competition=competition,
                season="N/A",
                match_date=match_date
            )
            self.match_repo.save(new_match)
        
        # 3. Dispatch Job (pass mode to task for highlight handling)
        job_id = self.dispatcher.start_processing(video_path, output_path, mode=mode)
        
        match_source = "existing" if existing_match else "created"
        return VideoJobResult(
            job_id=job_id,
            status="PENDING",
            message=f"Video processing job started for {match_id} (Match: {match_source}, Mode: {mode})"
        )
