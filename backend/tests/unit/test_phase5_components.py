"""
Unit Tests for Phase 5 Components

Tests for:
- HeuristicActionClassifier
- Lineup API utilities
"""
import pytest
from typing import List

# Import test subjects
from src.infrastructure.ml.action_classifier import (
    HeuristicActionClassifier, ActionType, ClassifiedAction
)
from src.domain.services.trajectory_smoother import TrajectoryPoint
from src.domain.services.scene_detector import Scene, SceneDetector, SceneDetectorConfig


# ==========================================
# HeuristicActionClassifier Tests
# ==========================================

class TestHeuristicActionClassifier:
    """Tests for HeuristicActionClassifier."""
    
    def test_classify_goal_area(self):
        """Test classification when ball is in goal area."""
        classifier = HeuristicActionClassifier(pitch_width=105.0, pitch_height=68.0)
        
        # Ball in away goal mouth (x > 100, y ~ 34)
        points = [
            TrajectoryPoint(frame_id=1, object_id=99, x=103.0, y=34.0, 
                           timestamp=0.04, object_type="ball"),
            TrajectoryPoint(frame_id=1, object_id=1, x=90.0, y=34.0,
                           timestamp=0.04, object_type="player"),
        ]
        
        result = classifier.classify_segment(points, 0, 5)
        
        # Should detect as goal or shot
        assert result.action_type in [ActionType.GOAL, ActionType.SHOT]
        assert result.confidence >= 0.5
    
    def test_classify_corner(self):
        """Test classification when ball is in corner."""
        classifier = HeuristicActionClassifier(pitch_width=105.0, pitch_height=68.0)
        
        # Ball in top-right corner
        points = [
            TrajectoryPoint(frame_id=1, object_id=99, x=102.0, y=66.0,
                           timestamp=0.04, object_type="ball"),
        ]
        
        result = classifier.classify_segment(points, 0, 5)
        
        assert result.action_type == ActionType.CORNER
    
    def test_classify_unknown(self):
        """Test classification with ball in midfield."""
        classifier = HeuristicActionClassifier()
        
        # Ball in center
        points = [
            TrajectoryPoint(frame_id=1, object_id=99, x=52.5, y=34.0,
                           timestamp=0.04, object_type="ball"),
        ]
        
        result = classifier.classify_segment(points, 0, 5)
        
        assert result.action_type == ActionType.UNKNOWN
    
    def test_empty_input(self):
        """Test with no tracking data."""
        classifier = HeuristicActionClassifier()
        
        result = classifier.classify_segment([], 0, 5)
        
        assert result.action_type == ActionType.UNKNOWN
        assert result.confidence == 0.0


# ==========================================
# SceneDetector Tests
# ==========================================

class TestSceneDetector:
    """Tests for SceneDetector."""
    
    def test_detect_single_scene(self):
        """Test detection with no cuts."""
        config = SceneDetectorConfig(difference_threshold=0.3, min_scene_frames=5)
        detector = SceneDetector(config)
        
        # All low differences (no cuts)
        diffs = [0.05] * 50
        
        scenes = detector.detect_scenes_from_diffs(diffs)
        
        assert len(scenes) == 1
        assert scenes[0].start_frame == 0
        assert scenes[0].end_frame == 51
    
    def test_detect_multiple_scenes(self):
        """Test detection with cuts."""
        config = SceneDetectorConfig(difference_threshold=0.3, min_scene_frames=5)
        detector = SceneDetector(config)
        
        # Two scenes with a cut at frame 25
        diffs = [0.05] * 24 + [0.5] + [0.05] * 25  # 50 diffs total
        
        scenes = detector.detect_scenes_from_diffs(diffs)
        
        assert len(scenes) == 2
        assert scenes[0].end_frame == 24
        assert scenes[1].start_frame == 25
    
    def test_filter_short_scenes(self):
        """Test that short scenes are filtered."""
        config = SceneDetectorConfig(difference_threshold=0.3, min_scene_frames=10)
        detector = SceneDetector(config)
        
        # Very short scenes (should be filtered)
        diffs = [0.05] * 5 + [0.5] + [0.05] * 5 + [0.5] + [0.05] * 30
        
        scenes = detector.detect_scenes_from_diffs(diffs)
        
        # Only the last scene should pass the filter
        assert len(scenes) == 1


# ==========================================
# Lineup Utilities Tests
# ==========================================

class TestLineupUtilities:
    """Tests for lineup utility functions."""
    
    def test_get_player_name(self):
        """Test getting player name by track ID."""
        from src.infrastructure.api.endpoints.lineup import (
            get_player_name, get_team_by_track, _lineup_storage, PlayerMapping
        )
        
        # Setup test data
        _lineup_storage["test-match"] = [
            PlayerMapping(track_id=1, player_name="Messi", jersey_number=10, team="home"),
            PlayerMapping(track_id=2, player_name="Mbappé", jersey_number=7, team="away"),
        ]
        
        # Test retrieval
        assert get_player_name("test-match", 1) == "Messi"
        assert get_player_name("test-match", 2) == "Mbappé"
        assert get_player_name("test-match", 99) is None
        assert get_player_name("unknown-match", 1) is None
        
        # Cleanup
        del _lineup_storage["test-match"]
    
    def test_get_team_by_track(self):
        """Test getting team by track ID."""
        from src.infrastructure.api.endpoints.lineup import (
            get_team_by_track, _lineup_storage, PlayerMapping
        )
        
        # Setup
        _lineup_storage["test-match"] = [
            PlayerMapping(track_id=1, player_name="Messi", team="home"),
        ]
        
        assert get_team_by_track("test-match", 1) == "home"
        assert get_team_by_track("test-match", 99) is None
        
        # Cleanup
        del _lineup_storage["test-match"]


# ==========================================
# Run Tests  
# ==========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
