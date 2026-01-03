"""
Action Classifier - Infrastructure Layer

Classifies detected actions/events in video clips.
MVP: Heuristic-based classification using spatial features.
Future: SlowFast/VideoMAE deep learning models.
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum
import logging

from src.domain.services.trajectory_smoother import TrajectoryPoint

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions that can be classified."""
    GOAL = "goal"
    SHOT = "shot"
    SAVE = "save"
    FOUL = "foul"
    CORNER = "corner"
    FREEKICK = "freekick"
    PENALTY = "penalty"
    CELEBRATION = "celebration"
    UNKNOWN = "unknown"


@dataclass
class ClassifiedAction:
    """A classified action in a video segment."""
    action_type: ActionType
    confidence: float
    frame_start: int
    frame_end: int
    description: str


@dataclass
class PitchZones:
    """Pitch zone definitions (normalized 0-1 coordinates)."""
    # Goal areas (penalty box)
    HOME_GOAL_AREA = (0.0, 0.165, 0.21, 0.835)  # (x1, y1, x2, y2)
    AWAY_GOAL_AREA = (0.835, 0.165, 1.0, 0.835)
    
    # Goal mouths (smaller, inside goal area)
    HOME_GOAL_MOUTH = (0.0, 0.367, 0.05, 0.633)
    AWAY_GOAL_MOUTH = (0.95, 0.367, 1.0, 0.633)
    
    # Corner zones
    CORNERS = [
        (0.0, 0.0, 0.05, 0.05),      # Home left
        (0.0, 0.95, 0.05, 1.0),      # Home right
        (0.95, 0.0, 1.0, 0.05),      # Away left
        (0.95, 0.95, 1.0, 1.0),      # Away right
    ]


class HeuristicActionClassifier:
    """
    MVP action classifier using spatial heuristics.
    
    Classifies actions based on:
    - Ball position (near goal = shot/goal)
    - Player density (celebration = clustered players)
    - Ball velocity (high velocity = shot)
    """
    
    def __init__(self, pitch_width: float = 105.0, pitch_height: float = 68.0):
        """Initialize with pitch dimensions."""
        self.pitch_width = pitch_width
        self.pitch_height = pitch_height
    
    def classify_segment(
        self, 
        tracking_points: List[TrajectoryPoint],
        frame_start: int,
        frame_end: int
    ) -> ClassifiedAction:
        """
        Classify an action in a video segment.
        
        Args:
            tracking_points: Tracking data for the segment
            frame_start: Start frame of segment
            frame_end: End frame of segment
            
        Returns:
            Classified action with confidence
        """
        if not tracking_points:
            return ClassifiedAction(
                action_type=ActionType.UNKNOWN,
                confidence=0.0,
                frame_start=frame_start,
                frame_end=frame_end,
                description="No tracking data"
            )
        
        # Filter to segment frames
        segment_points = [
            p for p in tracking_points 
            if frame_start <= p.frame_id <= frame_end
        ]
        
        if not segment_points:
            return ClassifiedAction(
                action_type=ActionType.UNKNOWN,
                confidence=0.0,
                frame_start=frame_start,
                frame_end=frame_end,
                description="No data in segment"
            )
        
        # Find ball positions
        ball_positions = [
            (p.x, p.y, p.frame_id) 
            for p in segment_points 
            if p.object_type == "ball"
        ]
        
        # Find player positions
        player_positions = [
            (p.x, p.y, p.frame_id, p.object_id) 
            for p in segment_points 
            if p.object_type != "ball"
        ]
        
        # Check for goal/shot (ball near goal)
        goal_result = self._check_goal_area(ball_positions)
        if goal_result:
            return ClassifiedAction(
                action_type=goal_result[0],
                confidence=goal_result[1],
                frame_start=frame_start,
                frame_end=frame_end,
                description=goal_result[2]
            )
        
        # Check for celebration (players clustered)
        celebration_result = self._check_celebration(player_positions)
        if celebration_result:
            return ClassifiedAction(
                action_type=ActionType.CELEBRATION,
                confidence=celebration_result[0],
                frame_start=frame_start,
                frame_end=frame_end,
                description=celebration_result[1]
            )
        
        # Check for corner (ball in corner zone)
        corner_result = self._check_corner(ball_positions)
        if corner_result:
            return ClassifiedAction(
                action_type=ActionType.CORNER,
                confidence=corner_result[0],
                frame_start=frame_start,
                frame_end=frame_end,
                description=corner_result[1]
            )
        
        # Default: Unknown
        return ClassifiedAction(
            action_type=ActionType.UNKNOWN,
            confidence=0.3,
            frame_start=frame_start,
            frame_end=frame_end,
            description="No specific action detected"
        )
    
    def _normalize_coords(self, x: float, y: float) -> Tuple[float, float]:
        """Normalize coordinates to 0-1 range."""
        return (x / self.pitch_width, y / self.pitch_height)
    
    def _check_goal_area(
        self, 
        ball_positions: List[Tuple]
    ) -> Optional[Tuple[ActionType, float, str]]:
        """Check if ball is in goal area (potential shot/goal)."""
        if not ball_positions:
            return None
        
        # Check last few positions
        recent = ball_positions[-5:] if len(ball_positions) >= 5 else ball_positions
        
        for x, y, frame_id in recent:
            nx, ny = self._normalize_coords(x, y)
            
            # Home goal mouth
            if nx < 0.05 and 0.367 < ny < 0.633:
                return (ActionType.GOAL, 0.8, "Ball in home goal mouth")
            
            # Away goal mouth
            if nx > 0.95 and 0.367 < ny < 0.633:
                return (ActionType.GOAL, 0.8, "Ball in away goal mouth")
            
            # Home penalty area
            if nx < 0.165 and 0.21 < ny < 0.835:
                return (ActionType.SHOT, 0.6, "Ball in home penalty area")
            
            # Away penalty area
            if nx > 0.835 and 0.21 < ny < 0.835:
                return (ActionType.SHOT, 0.6, "Ball in away penalty area")
        
        return None
    
    def _check_celebration(
        self, 
        player_positions: List[Tuple]
    ) -> Optional[Tuple[float, str]]:
        """Check for player clustering (celebration pattern)."""
        if len(player_positions) < 5:
            return None
        
        # Get last frame's positions
        last_frame = max(p[2] for p in player_positions)
        last_positions = [p for p in player_positions if p[2] == last_frame]
        
        if len(last_positions) < 3:
            return None
        
        # Calculate average position
        avg_x = sum(p[0] for p in last_positions) / len(last_positions)
        avg_y = sum(p[1] for p in last_positions) / len(last_positions)
        
        # Calculate average distance from center
        distances = [
            ((p[0] - avg_x)**2 + (p[1] - avg_y)**2)**0.5 
            for p in last_positions
        ]
        avg_distance = sum(distances) / len(distances)
        
        # If players are clustered (avg distance < 5m)
        if avg_distance < 5.0:
            return (0.7, f"Players clustered (avg distance: {avg_distance:.1f}m)")
        
        return None
    
    def _check_corner(
        self, 
        ball_positions: List[Tuple]
    ) -> Optional[Tuple[float, str]]:
        """Check if ball is in corner zone."""
        if not ball_positions:
            return None
        
        for x, y, frame_id in ball_positions:
            nx, ny = self._normalize_coords(x, y)
            
            # Check all corner zones
            for i, corner in enumerate(PitchZones.CORNERS):
                if (corner[0] <= nx <= corner[2] and 
                    corner[1] <= ny <= corner[3]):
                    corner_names = ["Home left", "Home right", "Away left", "Away right"]
                    return (0.7, f"Ball in {corner_names[i]} corner")
        
        return None
    
    def classify_scenes(
        self, 
        tracking_points: List[TrajectoryPoint],
        scenes: List[Tuple[int, int]]
    ) -> List[ClassifiedAction]:
        """
        Classify multiple scenes.
        
        Args:
            tracking_points: All tracking data
            scenes: List of (start_frame, end_frame) tuples
            
        Returns:
            List of classified actions for each scene
        """
        return [
            self.classify_segment(tracking_points, start, end)
            for start, end in scenes
        ]
