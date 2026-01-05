"""
Match API Endpoints - Infrastructure Layer

Endpoints for querying match data.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel

from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo

router = APIRouter(prefix="/api/v1/matches", tags=["matches"])

class MatchResponse(BaseModel):
    match_id: str
    home_team_id: str
    away_team_id: str
    event_count: int

@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: str):
    """
    Get match details by ID.
    
    Verifies that a match has been successfully ingested and persists in the DB.
    """
    repo = PostgresMatchRepo()
    match = repo.get_match(match_id, source="any")
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    return MatchResponse(
        match_id=match.match_id,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        event_count=len(match.events)
    )


class MatchListItem(BaseModel):
    match_id: str
    home_team_id: str
    away_team_id: str
    event_count: int
    date: Optional[str] = None
    score: Optional[str] = None


@router.get("", response_model=List[MatchListItem])
async def list_matches(limit: int = 20, offset: int = 0):
    """
    List all available matches.
    
    Returns a paginated list of matches that have been processed.
    """
    repo = PostgresMatchRepo()
    matches = repo.list_matches(limit=limit, offset=offset)
    
    return [
        MatchListItem(
            match_id=m.match_id,
            home_team_id=m.home_team_id,
            away_team_id=m.away_team_id,
            event_count=len(m.events) if m.events else 0,
            date=None,  # Add if available in match data
            score=None,  # Add if available in match data
        )
        for m in matches
    ]


class TrackingFrame(BaseModel):
    frame_id: int
    timestamp: float
    players: List[dict]
    ball: Optional[dict] = None


@router.get("/{match_id}/tracking", response_model=List[TrackingFrame])
async def get_tracking_data(
    match_id: str,
    start_frame: int = 0,
    end_frame: Optional[int] = None,
    sample_rate: int = 1
):
    """
    Get tracking data for a match.
    
    Returns player positions for each frame in the specified range.
    Use sample_rate to skip frames (e.g., sample_rate=5 returns every 5th frame).
    """
    from src.infrastructure.storage.minio_adapter import MinIOAdapter
    import json
    
    try:
        storage = MinIOAdapter()
        tracking_data = storage.get_tracking_data(match_id)
        
        if not tracking_data:
            return []
        
        # Filter by frame range
        if end_frame:
            tracking_data = [f for f in tracking_data if start_frame <= f.get('frame_id', 0) <= end_frame]
        else:
            tracking_data = [f for f in tracking_data if f.get('frame_id', 0) >= start_frame]
        
        # Sample frames
        tracking_data = tracking_data[::sample_rate]
        
        return [
            TrackingFrame(
                frame_id=f.get('frame_id', 0),
                timestamp=f.get('timestamp', 0.0),
                players=f.get('players', []),
                ball=f.get('ball'),
            )
            for f in tracking_data[:1000]  # Limit to 1000 frames max
        ]
    except Exception as e:
        # Return empty if no tracking data available
        return []


@router.get("/{match_id}/metrics")
async def get_match_metrics(match_id: str):
    """
    Get computed metrics for a match.
    
    Returns PPDA, pitch control, speeds, distances over time.
    """
    from src.infrastructure.db.repositories.postgres_metrics_repo import PostgresMetricsRepository
    
    try:
        repo = PostgresMetricsRepository()
        metrics = repo.get_metrics_by_match(match_id)
        
        if not metrics:
            return {
                "match_id": match_id,
                "status": "no_data",
                "message": "No metrics available. Run calculate-metrics first.",
                "metrics": {}
            }
        
        return {
            "match_id": match_id,
            "status": "available",
            "metrics": metrics
        }
    except Exception as e:
        return {
            "match_id": match_id,
            "status": "error",
            "message": str(e),
            "metrics": {}
        }
