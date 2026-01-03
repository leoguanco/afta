"""
LineupRepository Port - Domain Layer

Abstract interface for lineup persistence.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class PlayerMappingDTO:
    """Data transfer object for player mapping."""
    track_id: int
    player_name: str
    team: str
    jersey_number: Optional[int] = None


class LineupRepository(ABC):
    """
    Port for lineup persistence operations.
    """
    
    @abstractmethod
    def save_mappings(self, match_id: str, mappings: List[PlayerMappingDTO]) -> None:
        """
        Save player mappings for a match.
        
        Replaces any existing mappings for the match.
        """
        ...
    
    @abstractmethod
    def get_mappings(self, match_id: str) -> List[PlayerMappingDTO]:
        """
        Get all player mappings for a match.
        """
        ...
    
    @abstractmethod
    def get_player_name(self, match_id: str, track_id: int) -> Optional[str]:
        """
        Get player name by track ID.
        """
        ...
    
    @abstractmethod
    def get_team(self, match_id: str, track_id: int) -> Optional[str]:
        """
        Get team (home/away) by track ID.
        """
        ...
    
    @abstractmethod
    def delete_mappings(self, match_id: str) -> None:
        """
        Delete all mappings for a match.
        """
        ...
