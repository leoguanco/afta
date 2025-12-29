"""
PatternRepository - Domain Layer

Port for pattern persistence.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.tactical_pattern import TacticalPattern


class PatternRepository(ABC):
    """
    Abstract interface for pattern storage.
    
    Implementations handle persistence of discovered patterns.
    """
    
    @abstractmethod
    def save_patterns(self, patterns: List[TacticalPattern]) -> None:
        """
        Save discovered patterns.
        
        Args:
            patterns: List of TacticalPattern entities
        """
        ...
    
    @abstractmethod
    def get_patterns(self, match_id: str, team_id: str = None) -> List[TacticalPattern]:
        """
        Get patterns for a match.
        
        Args:
            match_id: Match identifier
            team_id: Optional team filter
            
        Returns:
            List of TacticalPattern entities
        """
        ...
    
    @abstractmethod
    def get_pattern_by_id(self, pattern_id: str) -> Optional[TacticalPattern]:
        """
        Get a single pattern by ID.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            TacticalPattern or None
        """
        ...
    
    @abstractmethod
    def get_pattern_examples(self, pattern_id: str, limit: int = 10) -> List[str]:
        """
        Get example sequence IDs for a pattern.
        
        Args:
            pattern_id: Pattern identifier
            limit: Maximum examples to return
            
        Returns:
            List of sequence IDs
        """
        ...
