"""
Calculate Match Metrics Use Case - Application Layer

Orchestrates the calculation of all tactical metrics for a match.
"""
from dataclasses import dataclass
from typing import List, Dict, Any

from src.domain.entities.player_trajectory import PlayerTrajectory, FramePosition
from src.domain.entities.match_frame import MatchFrame, PlayerPosition, BallPosition
from src.domain.entities.tactical_match import TacticalMatch, MatchEvent, EventType
from src.domain.ports.metrics_repository import MetricsRepository


@dataclass
class MetricsResult:
    """Result of metrics calculation."""
    match_id: str
    players_processed: int
    frames_processed: int
    events_processed: int
    status: str = "completed"


class CalculateMatchMetricsUseCase:
    """
    Application use case for calculating all tactical metrics.
    
    Orchestrates domain entities and persists results via repository port.
    """
    
    def __init__(self, metrics_repository: MetricsRepository):
        """
        Initialize use case.
        
        Args:
            metrics_repository: Repository port for persisting metrics
        """
        self.metrics_repository = metrics_repository
    
    def execute(
        self,
        match_id: str,
        tracking_data: List[Dict[str, Any]],
        event_data: List[Dict[str, Any]]
    ) -> MetricsResult:
        """
        Execute the use case to calculate all metrics.
        
        Args:
            match_id: Match identifier
            tracking_data: Raw tracking data (list of frame positions)
            event_data: Raw event data
            
        Returns:
            MetricsResult with calculation summary
        """
        # Process physical metrics (per player)
        player_trajectories = self._build_player_trajectories(tracking_data)
        for trajectory in player_trajectories:
            metrics = trajectory.calculate_physical_metrics()
            
            self.metrics_repository.save_physical_stats(
                match_id=match_id,
                player_id=trajectory.player_id,
                total_distance=metrics.total_distance,
                max_speed=metrics.max_speed,
                sprint_count=metrics.sprint_count,
                avg_speed=metrics.avg_speed
            )
        
        # Process pitch control (sampled frames)
        match_frames = self._build_match_frames(tracking_data, sample_rate=25)
        for frame in match_frames:
            pitch_control = frame.calculate_pitch_control()
            
            self.metrics_repository.save_pitch_control_frame(
                match_id=match_id,
                frame_id=frame.frame_id,
                home_control=pitch_control.home_control,
                away_control=pitch_control.away_control
            )
        
        # Process tactical metrics (PPDA, pressing)
        tactical_match = self._build_tactical_match(match_id, event_data)
        
        ppda_home = tactical_match.calculate_ppda("home", "away")
        ppda_away = tactical_match.calculate_ppda("away", "home")
        
        self.metrics_repository.save_ppda(
            match_id=match_id,
            team_id="home",
            passes_allowed=ppda_home.passes_allowed,
            defensive_actions=ppda_home.defensive_actions,
            ppda=ppda_home.ppda
        )
        
        self.metrics_repository.save_ppda(
            match_id=match_id,
            team_id="away",
            passes_allowed=ppda_away.passes_allowed,
            defensive_actions=ppda_away.defensive_actions,
            ppda=ppda_away.ppda
        )
        
        return MetricsResult(
            match_id=match_id,
            players_processed=len(player_trajectories),
            frames_processed=len(match_frames),
            events_processed=len(event_data)
        )
    
    def _build_player_trajectories(
        self,
        tracking_data: List[Dict[str, Any]]
    ) -> List[PlayerTrajectory]:
        """Build PlayerTrajectory entities from raw data."""
        # Group by player
        player_frames_dict: Dict[str, List[FramePosition]] = {}
        
        for data in tracking_data:
            player_id = data["player_id"]
            frame = FramePosition(
                frame_id=data["frame_id"],
                x=data["x"],
                y=data["y"],
                timestamp=data["timestamp"]
            )
            
            if player_id not in player_frames_dict:
                player_frames_dict[player_id] = []
            player_frames_dict[player_id].append(frame)
        
        # Create entities
        return [
            PlayerTrajectory(player_id, frames)
            for player_id, frames in player_frames_dict.items()
        ]
    
    def _build_match_frames(
        self,
        tracking_data: List[Dict[str, Any]],
        sample_rate: int = 25
    ) -> List[MatchFrame]:
        """Build MatchFrame entities from raw data (sampled)."""
        # Group by frame_id
        frames_dict: Dict[int, List[Dict[str, Any]]] = {}
        
        for data in tracking_data:
            frame_id = data["frame_id"]
            if frame_id not in frames_dict:
                frames_dict[frame_id] = []
            frames_dict[frame_id].append(data)
        
        # Sample and create entities
        match_frames = []
        for frame_id in sorted(frames_dict.keys()):
            if frame_id % sample_rate != 0:
                continue
            
            players = [
                PlayerPosition(
                    player_id=d["player_id"],
                    team_id=d["team_id"],
                    x=d["x"],
                    y=d["y"],
                    vx=d.get("vx", 0.0),
                    vy=d.get("vy", 0.0)
                )
                for d in frames_dict[frame_id]
            ]
            
            # Assume ball at center if not provided
            ball = BallPosition(x=52.5, y=34.0)
            
            match_frames.append(MatchFrame(frame_id, players, ball))
        
        return match_frames
    
    def _build_tactical_match(
        self,
        match_id: str,
        event_data: List[Dict[str, Any]]
    ) -> TacticalMatch:
        """Build TacticalMatch entity from raw data."""
        events = [
            MatchEvent(
                event_id=e["event_id"],
                event_type=EventType(e["event_type"]),
                team_id=e["team_id"],
                player_id=e["player_id"],
                timestamp=e["timestamp"],
                x=e["x"],
                y=e["y"]
            )
            for e in event_data
        ]
        
        return TacticalMatch(match_id, events)
