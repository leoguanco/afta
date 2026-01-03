"""
Lineup API Endpoints - Infrastructure Layer

Endpoints for managing player-track ID mappings.
Allows users to associate tracked player IDs with actual player names.
"""
from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/lineups", tags=["lineups"])


class PlayerMapping(BaseModel):
    """Mapping of a tracked player ID to player info."""
    track_id: int
    player_name: str
    jersey_number: Optional[int] = None
    team: str  # "home" or "away"


class LineupRequest(BaseModel):
    """Request to set lineup for a match."""
    match_id: str
    mappings: List[PlayerMapping]


class LineupResponse(BaseModel):
    """Response with current lineup mappings."""
    match_id: str
    mappings: List[PlayerMapping]
    total_tracks: int
    mapped_tracks: int


# In-memory storage (replace with DB in production)
_lineup_storage: Dict[str, List[PlayerMapping]] = {}


@router.post("", response_model=LineupResponse)
async def set_lineup(request: LineupRequest):
    """
    Set player lineup for a match.
    
    Maps tracked player IDs (1, 2, 3...) to actual player names.
    This allows events to be labeled with real player names.
    """
    _lineup_storage[request.match_id] = request.mappings
    
    return LineupResponse(
        match_id=request.match_id,
        mappings=request.mappings,
        total_tracks=len(request.mappings),
        mapped_tracks=len(request.mappings)
    )


@router.get("/{match_id}", response_model=LineupResponse)
async def get_lineup(match_id: str):
    """Get lineup mappings for a match."""
    if match_id not in _lineup_storage:
        raise HTTPException(status_code=404, detail="No lineup found for match")
    
    mappings = _lineup_storage[match_id]
    return LineupResponse(
        match_id=match_id,
        mappings=mappings,
        total_tracks=len(mappings),
        mapped_tracks=len(mappings)
    )


@router.delete("/{match_id}")
async def delete_lineup(match_id: str):
    """Delete lineup mappings for a match."""
    if match_id in _lineup_storage:
        del _lineup_storage[match_id]
    
    return {"status": "deleted", "match_id": match_id}


@router.get("/{match_id}/player/{track_id}")
async def get_player_by_track(match_id: str, track_id: int):
    """Get player info by track ID."""
    if match_id not in _lineup_storage:
        raise HTTPException(status_code=404, detail="No lineup found for match")
    
    mappings = _lineup_storage[match_id]
    for mapping in mappings:
        if mapping.track_id == track_id:
            return {
                "track_id": track_id,
                "player_name": mapping.player_name,
                "jersey_number": mapping.jersey_number,
                "team": mapping.team
            }
    
    raise HTTPException(status_code=404, detail=f"Track ID {track_id} not mapped")


def get_player_name(match_id: str, track_id: int) -> Optional[str]:
    """
    Utility function to get player name by track ID.
    
    Used by event generation to label events with player names.
    """
    if match_id not in _lineup_storage:
        return None
    
    for mapping in _lineup_storage[match_id]:
        if mapping.track_id == track_id:
            return mapping.player_name
    
    return None


def get_team_by_track(match_id: str, track_id: int) -> Optional[str]:
    """
    Get team (home/away) by track ID.
    
    Used by event generation to determine team associations.
    """
    if match_id not in _lineup_storage:
        return None
    
    for mapping in _lineup_storage[match_id]:
        if mapping.track_id == track_id:
            return mapping.team
    
    return None
