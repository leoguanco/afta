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
