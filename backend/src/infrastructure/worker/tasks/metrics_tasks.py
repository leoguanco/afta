"""
Metrics Tasks - Infrastructure Layer

Celery tasks for calculating tactical metrics in the background.
"""
from typing import List, Dict, Any
from celery import shared_task

# Domain services
from src.domain.services.physics import PhysicsService, FramePosition
from src.domain.services.pitch_control import PitchControlService, PlayerPosition
from src.domain.services.events import TacticalEventsService, MatchEvent, EventType

# Infrastructure
from src.infrastructure.storage.metrics_repo import MetricsRepository


@shared_task(name="calculate_match_metrics")
def calculate_match_metrics_task(
    match_id: str,
    tracking_data: List[Dict[str, Any]],
    event_data: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Calculate all tactical metrics for a match.
    
    This is the main orchestration task that:
    1. Invokes domain services to calculate metrics
    2. Saves results via repository
    
    Args:
        match_id: Match identifier
        tracking_data: List of tracking frames with player positions
        event_data: List of match events
        
    Returns:
        Status dictionary with calculation results
    """
    # Initialize services
    physics_service = PhysicsService()
    pitch_control_service = PitchControlService()
    events_service = TacticalEventsService()
    repository = MetricsRepository()
    
    # Group tracking data by player
    player_frames = _group_by_player(tracking_data)
    
    # Calculate physical metrics for each player
    for player_id, frames_data in player_frames.items():
        frames = [
            FramePosition(
                frame_id=f["frame_id"],
                player_id=f["player_id"],
                x=f["x"],
                y=f["y"],
                timestamp=f["timestamp"]
            )
            for f in frames_data
        ]
        
        metrics = physics_service.calculate_metrics(frames)
        
        repository.save_physical_stats(
            match_id=match_id,
            player_id=metrics.player_id,
            total_distance=metrics.total_distance,
            max_speed=metrics.max_speed,
            sprint_count=metrics.sprint_count,
            avg_speed=metrics.avg_speed
        )
    
    # Calculate pitch control for sample frames (every 25 frames = 1 second at 25fps)
    sample_frames = _get_sample_frames(tracking_data, sample_rate=25)
    
    for frame_id, frame_data in sample_frames.items():
        players = [
            PlayerPosition(
                player_id=p["player_id"],
                team_id=p["team_id"],
                x=p["x"],
                y=p["y"],
                vx=p.get("vx", 0.0),
                vy=p.get("vy", 0.0)
            )
            for p in frame_data["players"]
        ]
        
        ball_x = frame_data.get("ball_x", 52.5)
        ball_y = frame_data.get("ball_y", 34.0)
        
        pitch_control = pitch_control_service.calculate_pitch_control(
            players=players,
            ball_x=ball_x,
            ball_y=ball_y
        )
        
        repository.save_pitch_control_frame(
            match_id=match_id,
            frame_id=frame_id,
            home_control=pitch_control.home_control,
            away_control=pitch_control.away_control
        )
    
    # Calculate PPDA for both teams
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
    
    # Assume teams are "home" and "away"
    ppda_home = events_service.calculate_ppda(
        events=events,
        defending_team="home",
        attacking_team="away"
    )
    
    ppda_away = events_service.calculate_ppda(
        events=events,
        defending_team="away",
        attacking_team="home"
    )
    
    repository.save_ppda(
        match_id=match_id,
        team_id=ppda_home.team_id,
        passes_allowed=ppda_home.passes_allowed,
        defensive_actions=ppda_home.defensive_actions,
        ppda=ppda_home.ppda
    )
    
    repository.save_ppda(
        match_id=match_id,
        team_id=ppda_away.team_id,
        passes_allowed=ppda_away.passes_allowed,
        defensive_actions=ppda_away.defensive_actions,
        ppda=ppda_away.ppda
    )
    
    return {
        "status": "completed",
        "match_id": match_id,
        "players_processed": len(player_frames),
        "frames_processed": len(sample_frames),
        "events_processed": len(events)
    }


def _group_by_player(tracking_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group tracking data by player ID.
    
    Args:
        tracking_data: List of tracking frames
        
    Returns:
        Dictionary mapping player_id to list of frames
    """
    player_frames = {}
    
    for frame in tracking_data:
        player_id = frame["player_id"]
        if player_id not in player_frames:
            player_frames[player_id] = []
        player_frames[player_id].append(frame)
    
    return player_frames


def _get_sample_frames(
    tracking_data: List[Dict[str, Any]],
    sample_rate: int = 25
) -> Dict[int, Dict[str, Any]]:
    """
    Get sample frames for pitch control calculation.
    
    Args:
        tracking_data: List of tracking frames
        sample_rate: Sample every N frames
        
    Returns:
        Dictionary mapping frame_id to frame data
    """
    # Group by frame_id
    frames = {}
    for data in tracking_data:
        frame_id = data["frame_id"]
        if frame_id not in frames:
            frames[frame_id] = {"players": [], "frame_id": frame_id}
        frames[frame_id]["players"].append(data)
    
    # Sample frames
    sampled = {}
    for frame_id in sorted(frames.keys()):
        if frame_id % sample_rate == 0:
            sampled[frame_id] = frames[frame_id]
    
    return sampled
