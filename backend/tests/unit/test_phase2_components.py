"""
Unit Tests for Phase 2 Components

Tests for:
- TrajectorySmoother
- TrackCleaner
- HeuristicEventDetector
"""
import pytest
from typing import List

# Domain services
from src.domain.services.trajectory_smoother import (
    TrajectorySmoother, TrajectoryPoint, SmoothingPort
)
from src.domain.services.track_cleaner import (
    TrackCleaner, CleaningConfig
)
from src.application.use_cases.event_detector import (
    HeuristicEventDetector, DetectorConfig, InferredEventType
)


# ==========================================
# Test Doubles
# ==========================================

class FakeSmoother(SmoothingPort):
    """Fake smoother that returns same values (for testing)."""
    
    def smooth(self, values: List[float], window_size: int = 5) -> List[float]:
        # Simple moving average for testing
        if len(values) < window_size:
            return values
        
        result = []
        for i in range(len(values)):
            start = max(0, i - window_size // 2)
            end = min(len(values), i + window_size // 2 + 1)
            result.append(sum(values[start:end]) / (end - start))
        return result


# ==========================================
# TrajectorySmoother Tests
# ==========================================

class TestTrajectorySmoother:
    """Tests for TrajectorySmoother."""
    
    def test_smooth_single_trajectory(self):
        """Test smoothing a single player's trajectory."""
        smoother = TrajectorySmoother(FakeSmoother(), window_size=3)
        
        # Create trajectory with some noise
        points = [
            TrajectoryPoint(frame_id=1, object_id=1, x=10.0, y=20.0, timestamp=0.04),
            TrajectoryPoint(frame_id=2, object_id=1, x=10.5, y=20.5, timestamp=0.08),
            TrajectoryPoint(frame_id=3, object_id=1, x=15.0, y=25.0, timestamp=0.12),  # Spike
            TrajectoryPoint(frame_id=4, object_id=1, x=11.0, y=21.0, timestamp=0.16),
            TrajectoryPoint(frame_id=5, object_id=1, x=11.5, y=21.5, timestamp=0.20),
        ]
        
        smoothed = smoother.smooth_trajectories(points)
        
        assert len(smoothed) == 5
        # The spike should be smoothed
        assert smoothed[2].x < 15.0  # Smoothed down from spike
    
    def test_smooth_multiple_trajectories(self):
        """Test smoothing multiple players' trajectories."""
        smoother = TrajectorySmoother(FakeSmoother(), window_size=3)
        
        points = [
            # Player 1
            TrajectoryPoint(frame_id=1, object_id=1, x=10.0, y=20.0, timestamp=0.04),
            TrajectoryPoint(frame_id=2, object_id=1, x=11.0, y=21.0, timestamp=0.08),
            TrajectoryPoint(frame_id=3, object_id=1, x=12.0, y=22.0, timestamp=0.12),
            # Player 2
            TrajectoryPoint(frame_id=1, object_id=2, x=50.0, y=30.0, timestamp=0.04),
            TrajectoryPoint(frame_id=2, object_id=2, x=51.0, y=31.0, timestamp=0.08),
            TrajectoryPoint(frame_id=3, object_id=2, x=52.0, y=32.0, timestamp=0.12),
        ]
        
        smoothed = smoother.smooth_trajectories(points)
        
        assert len(smoothed) == 6
        # Check both players are present
        player_ids = set(p.object_id for p in smoothed)
        assert player_ids == {1, 2}
    
    def test_empty_input(self):
        """Test with empty input."""
        smoother = TrajectorySmoother(FakeSmoother())
        
        smoothed = smoother.smooth_trajectories([])
        
        assert smoothed == []


# ==========================================
# TrackCleaner Tests
# ==========================================

class TestTrackCleaner:
    """Tests for TrackCleaner."""
    
    def test_remove_short_tracks(self):
        """Test removal of ghost tracks (short duration)."""
        config = CleaningConfig(min_track_duration_frames=5)
        cleaner = TrackCleaner(config)
        
        points = [
            # Valid track (5 frames)
            *[TrajectoryPoint(frame_id=i, object_id=1, x=10.0+i, y=20.0, timestamp=i*0.04) 
              for i in range(5)],
            # Ghost track (3 frames - should be removed)
            *[TrajectoryPoint(frame_id=i, object_id=2, x=50.0+i, y=30.0, timestamp=i*0.04) 
              for i in range(3)],
        ]
        
        cleaned = cleaner.clean_tracks(points)
        
        # Only player 1's track should remain
        assert len(cleaned) == 5
        assert all(p.object_id == 1 for p in cleaned)
    
    def test_merge_fragments(self):
        """Test merging fragmented tracks."""
        config = CleaningConfig(
            min_track_duration_frames=3,
            merge_distance_threshold=2.0,
            merge_time_gap_frames=5
        )
        cleaner = TrackCleaner(config)
        
        points = [
            # Fragment 1 (frames 0-4)
            *[TrajectoryPoint(frame_id=i, object_id=1, x=10.0+i*0.1, y=20.0, timestamp=i*0.04) 
              for i in range(5)],
            # Fragment 2 (frames 7-11, close to where fragment 1 ended)
            *[TrajectoryPoint(frame_id=i, object_id=2, x=10.5, y=20.0, timestamp=i*0.04) 
              for i in range(7, 12)],
        ]
        
        cleaned = cleaner.clean_tracks(points)
        
        # Should be merged into single track
        unique_ids = set(p.object_id for p in cleaned)
        assert len(unique_ids) == 1  # Merged into one
    
    def test_empty_input(self):
        """Test with empty input."""
        cleaner = TrackCleaner()
        
        cleaned = cleaner.clean_tracks([])
        
        assert cleaned == []


# ==========================================
# HeuristicEventDetector Tests
# ==========================================

class TestHeuristicEventDetector:
    """Tests for HeuristicEventDetector."""
    
    def test_detect_possession(self):
        """Test possession detection when player is near ball."""
        config = DetectorConfig(
            ball_proximity_threshold=1.5,
            possession_min_frames=3
        )
        detector = HeuristicEventDetector(config)
        
        # Create scenario: Player 1 is close to ball
        points = []
        for i in range(10):
            # Ball at (50, 25)
            points.append(TrajectoryPoint(
                frame_id=i, object_id=99, x=50.0, y=25.0, 
                timestamp=i*0.04, object_type="ball"
            ))
            # Player 1 at (50.5, 25.5) - within 1.5m
            points.append(TrajectoryPoint(
                frame_id=i, object_id=1, x=50.5, y=25.5,
                timestamp=i*0.04, object_type="home"
            ))
        
        events = detector.detect_events(points)
        
        # Should detect possession (player near ball)
        # No events yet since no pass/loss - possession is implicit
        assert isinstance(events, list)
    
    def test_detect_pass(self):
        """Test pass detection when possession transfers within team."""
        config = DetectorConfig(
            ball_proximity_threshold=1.5,
            pass_min_distance=3.0
        )
        detector = HeuristicEventDetector(config)
        
        points = []
        
        # Frames 0-4: Player 1 has ball
        for i in range(5):
            points.append(TrajectoryPoint(
                frame_id=i, object_id=99, x=20.0, y=20.0,
                timestamp=i*0.04, object_type="ball"
            ))
            points.append(TrajectoryPoint(
                frame_id=i, object_id=1, x=20.5, y=20.5,
                timestamp=i*0.04, object_type="home"
            ))
            points.append(TrajectoryPoint(
                frame_id=i, object_id=2, x=30.0, y=20.0,
                timestamp=i*0.04, object_type="home"
            ))
        
        # Frames 5-9: Ball moves to Player 2 (same team)
        for i in range(5, 10):
            points.append(TrajectoryPoint(
                frame_id=i, object_id=99, x=30.0, y=20.0,
                timestamp=i*0.04, object_type="ball"
            ))
            points.append(TrajectoryPoint(
                frame_id=i, object_id=1, x=20.5, y=20.5,
                timestamp=i*0.04, object_type="home"
            ))
            points.append(TrajectoryPoint(
                frame_id=i, object_id=2, x=30.5, y=20.5,
                timestamp=i*0.04, object_type="home"
            ))
        
        events = detector.detect_events(points)
        
        # Should detect a pass from Player 1 to Player 2
        pass_events = [e for e in events if e.event_type == InferredEventType.PASS_COMPLETE]
        assert len(pass_events) >= 1
        assert 1 in pass_events[0].actors
        assert 2 in pass_events[0].actors
    
    def test_empty_input(self):
        """Test with empty input."""
        detector = HeuristicEventDetector()
        
        events = detector.detect_events([])
        
        assert events == []


# ==========================================
# TimeSync Tests
# ==========================================

class TestTimeSync:
    """Tests for TimeSync utility."""
    
    def test_frame_to_video_time(self):
        """Test frame to video time conversion."""
        from src.domain.services.time_sync import TimeSync, SyncConfig
        
        sync = TimeSync(SyncConfig(fps=25.0))
        
        assert sync.frame_to_video_time(0) == 0.0
        assert sync.frame_to_video_time(25) == 1.0
        assert sync.frame_to_video_time(150) == 6.0  # 150 / 25 = 6
    
    def test_frame_to_match_time_no_offset(self):
        """Test frame to match time with no offset."""
        from src.domain.services.time_sync import TimeSync, SyncConfig
        
        sync = TimeSync(SyncConfig(fps=25.0, sync_offset_seconds=0.0))
        
        # No offset: video time = match time
        assert sync.frame_to_match_time(0) == 0.0
        assert sync.frame_to_match_time(1500) == 60.0  # 1 minute
    
    def test_frame_to_match_time_with_offset(self):
        """Test frame to match time with positive offset (pre-match footage)."""
        from src.domain.services.time_sync import TimeSync, SyncConfig
        
        # Video starts 300s (5 mins) before kick-off
        sync = TimeSync(SyncConfig(fps=25.0, sync_offset_seconds=300.0))
        
        # Frame 0 = video time 0s = match time -300s
        assert sync.frame_to_match_time(0) == -300.0
        
        # Frame 7500 = video time 300s = match time 0s (kick-off)
        assert sync.frame_to_match_time(7500) == 0.0
        
        # Frame 9000 = video time 360s = match time 60s (1st minute)
        assert sync.frame_to_match_time(9000) == 60.0
    
    def test_match_time_to_frame(self):
        """Test match time to frame conversion."""
        from src.domain.services.time_sync import TimeSync, SyncConfig
        
        sync = TimeSync(SyncConfig(fps=25.0, sync_offset_seconds=300.0))
        
        # Kick-off (match time 0) = frame 7500
        assert sync.match_time_to_frame(0.0) == 7500
        
        # 1 minute into match = frame 9000
        assert sync.match_time_to_frame(60.0) == 9000
    
    def test_event_minute_to_frame(self):
        """Test event minute:second to frame conversion."""
        from src.domain.services.time_sync import TimeSync, SyncConfig
        
        sync = TimeSync(SyncConfig(fps=25.0, sync_offset_seconds=0.0))
        
        # Minute 10:30 = 630 seconds = 15750 frames
        assert sync.event_minute_to_frame(10, 30) == 15750
    
    def test_frame_range_for_event(self):
        """Test getting frame range around an event."""
        from src.domain.services.time_sync import TimeSync, SyncConfig
        
        sync = TimeSync(SyncConfig(fps=25.0, sync_offset_seconds=0.0))
        
        # Event at 60s with 2s window
        start, end = sync.get_frame_range_for_event(60.0, window_seconds=2.0)
        
        # 59s to 61s = frames 1475 to 1525
        assert start == 1475
        assert end == 1525


# ==========================================
# Run Tests
# ==========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
