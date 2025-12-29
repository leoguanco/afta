"""
PatternDetectorPort - Domain Layer

Port for pattern detection via clustering.
"""
from abc import ABC, abstractmethod
from typing import List

from src.domain.entities.possession_sequence import PossessionSequence
from src.domain.entities.tactical_pattern import TacticalPattern


class PatternDetectorPort(ABC):
    """
    Abstract interface for pattern detection.
    
    Implementations will use clustering algorithms (K-means, DBSCAN, etc.)
    to discover tactical patterns from possession sequences.
    """
    
    @abstractmethod
    def fit(self, sequences: List[PossessionSequence], n_clusters: int = 8) -> None:
        """
        Fit the clustering model on sequences.
        
        Args:
            sequences: List of possession sequences
            n_clusters: Number of clusters (for K-means)
        """
        ...
    
    @abstractmethod
    def predict_cluster(self, sequence: PossessionSequence) -> int:
        """
        Predict cluster label for a single sequence.
        
        Args:
            sequence: Possession sequence
            
        Returns:
            Cluster label (integer)
        """
        ...
    
    @abstractmethod
    def get_patterns(
        self,
        sequences: List[PossessionSequence],
        match_id: str,
        team_id: str
    ) -> List[TacticalPattern]:
        """
        Get discovered patterns after fitting.
        
        Args:
            sequences: Original sequences used for fitting
            match_id: Match identifier
            team_id: Team identifier
            
        Returns:
            List of TacticalPattern entities
        """
        ...
