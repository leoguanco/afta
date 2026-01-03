"""
Time Sync Utility - Domain Service

Converts between video frame numbers and match timestamps.
Used for aligning video tracking data with event data (e.g., StatsBomb).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class SyncConfig:
    """Configuration for time synchronization."""
    fps: float = 25.0  # Video frames per second
    sync_offset_seconds: float = 0.0  # How much the video is offset from match time


class TimeSync:
    """
    Domain service for synchronizing video frames with match time.
    
    Video time: Frame 0 starts at second 0 of the video file.
    Match time: Second 0 is kick-off.
    
    sync_offset_seconds: If positive, video starts BEFORE kick-off.
                         If negative, video starts AFTER kick-off.
    
    Example:
        - Video has 5 minutes of pre-match footage before kick-off
        - sync_offset_seconds = 300 (5 * 60)
        - Frame 0 (video time 0s) = Match time -300s (5 mins before kick-off)
        - Frame 7500 (video time 300s @ 25fps) = Match time 0s (kick-off)
    """
    
    def __init__(self, config: SyncConfig = None):
        """Initialize with sync configuration."""
        self.config = config or SyncConfig()
    
    def frame_to_video_time(self, frame_id: int) -> float:
        """
        Convert frame number to video time in seconds.
        
        Args:
            frame_id: Frame number (0-indexed)
            
        Returns:
            Time in seconds since video start
        """
        return frame_id / self.config.fps
    
    def frame_to_match_time(self, frame_id: int) -> float:
        """
        Convert frame number to match time in seconds.
        
        Args:
            frame_id: Frame number (0-indexed)
            
        Returns:
            Time in seconds since kick-off (can be negative)
        """
        video_time = self.frame_to_video_time(frame_id)
        return video_time - self.config.sync_offset_seconds
    
    def match_time_to_frame(self, match_time_seconds: float) -> int:
        """
        Convert match time to frame number.
        
        Args:
            match_time_seconds: Time since kick-off
            
        Returns:
            Frame number (rounded to nearest frame)
        """
        video_time = match_time_seconds + self.config.sync_offset_seconds
        return round(video_time * self.config.fps)
    
    def event_minute_to_frame(self, minute: int, second: int = 0) -> int:
        """
        Convert event time (minute:second) to frame number.
        
        Args:
            minute: Match minute (0 = kick-off)
            second: Seconds within minute
            
        Returns:
            Frame number
        """
        match_time_seconds = minute * 60 + second
        return self.match_time_to_frame(match_time_seconds)
    
    def frame_to_event_time(self, frame_id: int) -> tuple:
        """
        Convert frame to event time (minute, second).
        
        Args:
            frame_id: Frame number
            
        Returns:
            Tuple of (minute, second)
        """
        match_time = self.frame_to_match_time(frame_id)
        
        if match_time < 0:
            # Before kick-off
            return (0, 0)
        
        minute = int(match_time // 60)
        second = int(match_time % 60)
        return (minute, second)
    
    def get_frame_range_for_event(
        self, 
        event_timestamp: float,
        window_seconds: float = 2.0
    ) -> tuple:
        """
        Get frame range around an event for video analysis.
        
        Args:
            event_timestamp: Event time in seconds since kick-off
            window_seconds: Window size around event (default 2s)
            
        Returns:
            Tuple of (start_frame, end_frame)
        """
        half_window = window_seconds / 2
        start_frame = self.match_time_to_frame(event_timestamp - half_window)
        end_frame = self.match_time_to_frame(event_timestamp + half_window)
        return (max(0, start_frame), end_frame)
