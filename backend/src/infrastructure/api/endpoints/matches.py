"""
Match API Endpoints - Infrastructure Layer

Endpoints for querying match data.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel

from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
from src.infrastructure.storage.minio_adapter import MinIOAdapter

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
    import time
    
    # Global cache for tracking data
    # Key: match_id, Value: (data, timestamp)
    # We use a simple global dict since we want to share across requests
    # In a real prod app, use Redis or robust cache
    if not hasattr(get_tracking_data, "_cache"):
        get_tracking_data._cache = {}
        
    def _get_tracking_data_safe(mid: str):
        # 5 minute TTL
        now = time.time()
        if mid in get_tracking_data._cache:
            data, ts = get_tracking_data._cache[mid]
            if now - ts < 300:
                return data
            else:
                del get_tracking_data._cache[mid]
        
        try:
            storage = MinIOAdapter()
            data = storage.get_tracking_data(mid)
            if data:
                get_tracking_data._cache[mid] = (data, now)
            return data
        except Exception:
            return None

    tracking_data = _get_tracking_data_safe(match_id)
        
    if not tracking_data:
        return []
    
    # 1. Filter by range first to reduce processing
    if end_frame is not None:
        filtered_records = [r for r in tracking_data if start_frame <= r.get('frame_id', 0) <= end_frame]
    else:
        filtered_records = [r for r in tracking_data if r.get('frame_id', 0) >= start_frame]

    # 2. Group by frame_id
    grouped_frames = {}
    
    for record in filtered_records:
        fid = record.get('frame_id', 0)
        
        if fid not in grouped_frames:
            grouped_frames[fid] = {
                "frame_id": fid,
                # Use timestamp from the first record of the frame
                "timestamp": record.get('timestamp', fid * 0.04), 
                "players": [],
                "ball": None
            }
            
        # Check if it's a ball or player
        obj_type = record.get('object_type')
        
        # Check if text is 'ball' or if int is 0 (assuming 0 is ball class)
        is_ball = (
            str(obj_type).lower() == 'ball' or 
            obj_type == 0
        )
        
        if is_ball:
            grouped_frames[fid]['ball'] = {
                "x": record.get('x', 0), 
                "y": record.get('y', 0)
            }
        else:
            # It's a player
            grouped_frames[fid]['players'].append({
                "player_id": str(record.get('player_id', '')),
                "team": record.get('team', 'home'), # Default to home if missing
                "x": record.get('x', 0),
                "y": record.get('y', 0),
                "jersey_number": record.get('jersey_number')
            })

    # 3. Convert to list and Apply sample rate
    sorted_frames = sorted(grouped_frames.values(), key=lambda x: x['frame_id'])
    sampled_frames = sorted_frames[::sample_rate]
    
    # 4. Limit result size
    return [
        TrackingFrame(**f) for f in sampled_frames[:1000] 
    ]


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
