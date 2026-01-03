"""
Heuristic Event Detector - Application Layer

Infers semantic events (Possession, Pass, Pressure) from tracking data.
Uses rule-based heuristics based on player-ball proximity and velocity.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from enum import Enum

from src.domain.services.trajectory_smoother import TrajectoryPoint


class InferredEventType(Enum):
    """Event types that can be inferred from tracking."""
    POSSESSION = "possession"
    PASS_ATTEMPT = "pass_attempt" 
    PASS_COMPLETE = "pass_complete"
    PRESSURE = "pressure"
    LOSS_OF_POSSESSION = "loss_of_possession"


@dataclass
class InferredEvent:
    """An event inferred from tracking data."""
    frame_start: int
    frame_end: int
    event_type: InferredEventType
    actors: List[int]  # player IDs involved
    team_id: str
    location: Tuple[float, float]
    confidence: float = 1.0
    actor_names: List[str] = field(default_factory=list)  # Player names if available


@dataclass 
class PossessionState:
    """Tracks current possession state."""
    player_id: Optional[int] = None
    team_id: Optional[str] = None
    start_frame: int = 0
    x: float = 0.0
    y: float = 0.0


@dataclass
class DetectorConfig:
    """Configuration for event detection."""
    ball_proximity_threshold: float = 1.5  # meters to be "on ball"
    possession_min_frames: int = 3  # min frames to count as possession
    pressure_distance: float = 2.0  # meters for pressure
    pressure_min_velocity: float = 3.0  # m/s approaching ball carrier
    pass_min_distance: float = 3.0  # min meters for pass vs dribble


class HeuristicEventDetector:
    """
    Infers match events from tracking data using heuristics.
    
    Follows state machine: None -> Possession(P) -> Pass -> Possession(Q)
    """
    
    def __init__(self, config: DetectorConfig = None):
        """Initialize detector with config."""
        self.config = config or DetectorConfig()
    
    def detect_events(
        self, 
        tracking_points: List[TrajectoryPoint]
    ) -> List[InferredEvent]:
        """
        Detect events from tracking data.
        
        Args:
            tracking_points: Smoothed/cleaned tracking points
            
        Returns:
            List of inferred events
        """
        if not tracking_points:
            return []
        
        # Group by frame
        frames = self._group_by_frame(tracking_points)
        
        events = []
        possession = PossessionState()
        
        for frame_id in sorted(frames.keys()):
            frame_data = frames[frame_id]
            
            # Find ball position
            ball = self._find_ball(frame_data)
            if not ball:
                continue
            
            # Find closest player to ball
            closest = self._find_closest_player(frame_data, ball)
            if not closest:
                continue
            
            player_id, distance, player_point = closest
            
            # Check possession
            if distance <= self.config.ball_proximity_threshold:
                if possession.player_id is None:
                    # New possession
                    possession = PossessionState(
                        player_id=player_id,
                        team_id=player_point.object_type,  # Using object_type as team proxy
                        start_frame=frame_id,
                        x=player_point.x,
                        y=player_point.y
                    )
                elif possession.player_id != player_id:
                    # Possession changed
                    # Check if same team (pass) or different team (loss)
                    if possession.team_id == player_point.object_type:
                        # Same team = Pass
                        pass_distance = (
                            (player_point.x - possession.x) ** 2 +
                            (player_point.y - possession.y) ** 2
                        ) ** 0.5
                        
                        if pass_distance >= self.config.pass_min_distance:
                            events.append(InferredEvent(
                                frame_start=possession.start_frame,
                                frame_end=frame_id,
                                event_type=InferredEventType.PASS_COMPLETE,
                                actors=[possession.player_id, player_id],
                                team_id=possession.team_id or "unknown",
                                location=(possession.x, possession.y)
                            ))
                    else:
                        # Different team = Loss of possession
                        events.append(InferredEvent(
                            frame_start=possession.start_frame,
                            frame_end=frame_id,
                            event_type=InferredEventType.LOSS_OF_POSSESSION,
                            actors=[possession.player_id, player_id],
                            team_id=possession.team_id or "unknown",
                            location=(possession.x, possession.y)
                        ))
                    
                    # New possession
                    possession = PossessionState(
                        player_id=player_id,
                        team_id=player_point.object_type,
                        start_frame=frame_id,
                        x=player_point.x,
                        y=player_point.y
                    )
            
            # Check for pressure events
            if possession.player_id is not None:
                pressure_events = self._detect_pressure(
                    frame_data, possession, frame_id
                )
                events.extend(pressure_events)
        
        return events
    
    def _group_by_frame(
        self, 
        points: List[TrajectoryPoint]
    ) -> Dict[int, List[TrajectoryPoint]]:
        """Group tracking points by frame_id."""
        frames: Dict[int, List[TrajectoryPoint]] = {}
        for point in points:
            if point.frame_id not in frames:
                frames[point.frame_id] = []
            frames[point.frame_id].append(point)
        return frames
    
    def _find_ball(
        self, 
        frame_data: List[TrajectoryPoint]
    ) -> Optional[TrajectoryPoint]:
        """Find ball in frame data."""
        for point in frame_data:
            if point.object_type == "ball":
                return point
        return None
    
    def _find_closest_player(
        self, 
        frame_data: List[TrajectoryPoint],
        ball: TrajectoryPoint
    ) -> Optional[Tuple[int, float, TrajectoryPoint]]:
        """Find closest player to ball."""
        closest = None
        min_distance = float('inf')
        
        for point in frame_data:
            if point.object_type == "ball":
                continue
            
            distance = (
                (point.x - ball.x) ** 2 + 
                (point.y - ball.y) ** 2
            ) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest = (point.object_id, distance, point)
        
        return closest
    
    def _detect_pressure(
        self,
        frame_data: List[TrajectoryPoint],
        possession: PossessionState,
        frame_id: int
    ) -> List[InferredEvent]:
        """Detect pressure events on ball carrier."""
        events = []
        
        for point in frame_data:
            # Skip ball and possessing player
            if point.object_type == "ball" or point.object_id == possession.player_id:
                continue
            
            # Skip same team
            if point.object_type == possession.team_id:
                continue
            
            # Check distance to ball carrier
            distance = (
                (point.x - possession.x) ** 2 +
                (point.y - possession.y) ** 2
            ) ** 0.5
            
            if distance <= self.config.pressure_distance:
                events.append(InferredEvent(
                    frame_start=frame_id,
                    frame_end=frame_id,
                    event_type=InferredEventType.PRESSURE,
                    actors=[point.object_id, possession.player_id],
                    team_id=point.object_type,
                    location=(point.x, point.y),
                    confidence=0.8
                ))
        
        return events
    
    def detect_events_with_names(
        self,
        tracking_points: List[TrajectoryPoint],
        match_id: str
    ) -> List[InferredEvent]:
        """
        Detect events and resolve player names from lineup.
        
        Args:
            tracking_points: Smoothed/cleaned tracking points
            match_id: Match ID for lineup lookup
            
        Returns:
            List of inferred events with player names
        """
        # Import here to avoid circular dependency
        from src.infrastructure.api.endpoints.lineup import get_player_name
        
        events = self.detect_events(tracking_points)
        
        # Resolve player names for each event
        for event in events:
            names = []
            for actor_id in event.actors:
                name = get_player_name(match_id, actor_id)
                names.append(name if name else f"Player {actor_id}")
            event.actor_names = names
        
        return events

