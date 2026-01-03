"""
Lineup API Endpoints - Infrastructure Layer

Endpoints for managing player-track ID mappings.
Allows users to associate tracked player IDs with actual player names.
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from src.domain.ports.lineup_repository import PlayerMappingDTO
from src.infrastructure.db.repositories.postgres_lineup_repo import PostgresLineupRepository

router = APIRouter(prefix="/api/v1/lineups", tags=["lineups"])
logger = logging.getLogger(__name__)

# Singleton repository instance
_lineup_repo: Optional[PostgresLineupRepository] = None


def _get_repo() -> PostgresLineupRepository:
    """Get or create repository instance."""
    global _lineup_repo
    if _lineup_repo is None:
        _lineup_repo = PostgresLineupRepository()
    return _lineup_repo


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


@router.post("", response_model=LineupResponse)
async def set_lineup(request: LineupRequest):
    """
    Set player lineup for a match.
    
    Maps tracked player IDs (1, 2, 3...) to actual player names.
    This allows events to be labeled with real player names.
    Persists to PostgreSQL database.
    """
    repo = _get_repo()
    
    # Convert to DTOs
    dtos = [
        PlayerMappingDTO(
            track_id=m.track_id,
            player_name=m.player_name,
            jersey_number=m.jersey_number,
            team=m.team
        )
        for m in request.mappings
    ]
    
    repo.save_mappings(request.match_id, dtos)
    
    return LineupResponse(
        match_id=request.match_id,
        mappings=request.mappings,
        total_tracks=len(request.mappings),
        mapped_tracks=len(request.mappings)
    )


@router.get("/{match_id}", response_model=LineupResponse)
async def get_lineup(match_id: str):
    """Get lineup mappings for a match from database."""
    repo = _get_repo()
    dtos = repo.get_mappings(match_id)
    
    if not dtos:
        raise HTTPException(status_code=404, detail="No lineup found for match")
    
    mappings = [
        PlayerMapping(
            track_id=d.track_id,
            player_name=d.player_name,
            jersey_number=d.jersey_number,
            team=d.team
        )
        for d in dtos
    ]
    
    return LineupResponse(
        match_id=match_id,
        mappings=mappings,
        total_tracks=len(mappings),
        mapped_tracks=len(mappings)
    )


@router.delete("/{match_id}")
async def delete_lineup(match_id: str):
    """Delete lineup mappings for a match from database."""
    repo = _get_repo()
    repo.delete_mappings(match_id)
    
    return {"status": "deleted", "match_id": match_id}


@router.get("/{match_id}/player/{track_id}")
async def get_player_by_track(match_id: str, track_id: int):
    """Get player info by track ID from database."""
    repo = _get_repo()
    name = repo.get_player_name(match_id, track_id)
    
    if not name:
        raise HTTPException(status_code=404, detail=f"Track ID {track_id} not mapped")
    
    team = repo.get_team(match_id, track_id)
    
    return {
        "track_id": track_id,
        "player_name": name,
        "team": team
    }


def get_player_name(match_id: str, track_id: int) -> Optional[str]:
    """
    Utility function to get player name by track ID.
    
    Used by event generation to label events with player names.
    Now uses PostgreSQL for persistence.
    """
    try:
        repo = _get_repo()
        return repo.get_player_name(match_id, track_id)
    except Exception as e:
        logger.warning(f"Failed to get player name: {e}")
        return None


def get_team_by_track(match_id: str, track_id: int) -> Optional[str]:
    """
    Get team (home/away) by track ID.
    
    Used by event generation to determine team associations.
    Now uses PostgreSQL for persistence.
    """
    try:
        repo = _get_repo()
        return repo.get_team(match_id, track_id)
    except Exception as e:
        logger.warning(f"Failed to get team: {e}")
        return None
