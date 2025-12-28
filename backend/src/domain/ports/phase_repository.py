"""
PhaseRepository Port - Domain Layer

Interface for storing and retrieving phase classification data.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.phase_sequence import PhaseSequence, PhaseTransition
from src.domain.value_objects.game_phase import GamePhase


class PhaseRepository(ABC):
    """
    Port for phase sequence persistence.
    
    This interface allows different storage implementations
    (PostgreSQL, Redis cache, file-based, etc.).
    """
    
    @abstractmethod
    def save_phase_sequence(self, sequence: PhaseSequence) -> None:
        """
        Save a complete phase sequence for a match.
        
        Args:
            sequence: PhaseSequence entity to persist
        """
        pass
    
    @abstractmethod
    def get_phase_sequence(
        self, 
        match_id: str, 
        team_id: str = "home"
    ) -> Optional[PhaseSequence]:
        """
        Retrieve phase sequence for a match.
        
        Args:
            match_id: Match identifier
            team_id: Team perspective (home/away)
            
        Returns:
            PhaseSequence if exists, None otherwise
        """
        pass
    
    @abstractmethod
    def get_phases_in_range(
        self,
        match_id: str,
        team_id: str,
        start_frame: int,
        end_frame: Optional[int]
    ) -> List[dict]:
        """
        Get phase labels for a frame range.
        
        Args:
            match_id: Match identifier
            team_id: Team perspective
            start_frame: First frame (inclusive)
            end_frame: Last frame (inclusive), None for all remaining
            
        Returns:
            List of {frame_id, phase, confidence}
        """
        pass
    
    @abstractmethod
    def get_transitions(
        self,
        match_id: str,
        team_id: str
    ) -> List[PhaseTransition]:
        """
        Get all phase transitions for a match.
        
        Args:
            match_id: Match identifier
            team_id: Team perspective
            
        Returns:
            List of PhaseTransition objects
        """
        pass
    
    @abstractmethod
    def has_classification(self, match_id: str, team_id: str = "home") -> bool:
        """
        Check if phase classification exists for a match.
        
        Args:
            match_id: Match identifier
            team_id: Team perspective
            
        Returns:
            True if classification data exists
        """
        pass
    
    @abstractmethod
    def delete_phase_sequence(self, match_id: str, team_id: str = "home") -> bool:
        """
        Delete phase classification data for a match.
        
        Args:
            match_id: Match identifier
            team_id: Team perspective
            
        Returns:
            True if deleted, False if not found
        """
        pass
