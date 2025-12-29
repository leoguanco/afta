"""
PatternDetector - Application Layer

Use Case for detecting tactical patterns from match data.
"""
from dataclasses import dataclass
from typing import List, Optional

from src.domain.entities.tactical_pattern import TacticalPattern
from src.domain.entities.possession_sequence import PossessionSequence
from src.domain.entities.sequence_extractor import SequenceExtractor
from src.domain.ports.pattern_detector_port import PatternDetectorPort
from src.domain.ports.pattern_repository import PatternRepository
from src.domain.ports.match_repository import MatchRepository


@dataclass
class PatternDetectionResult:
    """Result of pattern detection."""
    match_id: str
    team_id: str
    pattern_count: int
    sequence_count: int
    patterns: List[TacticalPattern]


class PatternDetector:
    """
    Use Case: Detect Tactical Patterns.
    
    Orchestrates:
    1. Loading match events
    2. Extracting possession sequences
    3. Clustering sequences
    4. Labeling patterns
    5. Persisting results
    """
    
    def __init__(
        self,
        detector: PatternDetectorPort,
        pattern_repository: Optional[PatternRepository] = None,
        match_repository: Optional[MatchRepository] = None
    ):
        """
        Initialize with dependencies.
        
        Args:
            detector: ML pattern detection port
            pattern_repository: Optional pattern storage
            match_repository: Optional match data access
        """
        self.detector = detector
        self.pattern_repository = pattern_repository
        self.match_repository = match_repository
        self.sequence_extractor = SequenceExtractor()
    
    def execute(
        self,
        match_id: str,
        team_id: str = "home",
        n_clusters: int = 8,
        events: Optional[List[dict]] = None
    ) -> PatternDetectionResult:
        """
        Detect patterns in a match.
        
        Args:
            match_id: Match identifier
            team_id: Team perspective for filtering
            n_clusters: Number of pattern clusters
            events: Optional pre-loaded events (else loads from repo)
            
        Returns:
            PatternDetectionResult with discovered patterns
        """
        # Load events if not provided
        if events is None and self.match_repository:
            match = self.match_repository.get_match(match_id)
            if match:
                events = [e.__dict__ for e in match.events]
            else:
                events = []
        
        if not events:
            return PatternDetectionResult(
                match_id=match_id,
                team_id=team_id,
                pattern_count=0,
                sequence_count=0,
                patterns=[]
            )
        
        # Extract sequences
        all_sequences = self.sequence_extractor.extract(events, match_id)
        
        # Filter by team
        team_sequences = [
            s for s in all_sequences 
            if s.team_id == team_id or team_id == "all"
        ]
        
        if len(team_sequences) < n_clusters:
            # Not enough sequences for clustering
            n_clusters = max(2, len(team_sequences) // 2)
        
        # Fit clustering model
        self.detector.fit(team_sequences, n_clusters=n_clusters)
        
        # Get patterns
        patterns = self.detector.get_patterns(team_sequences, match_id, team_id)
        
        # Persist if repository available
        if self.pattern_repository and patterns:
            self.pattern_repository.save_patterns(patterns)
        
        return PatternDetectionResult(
            match_id=match_id,
            team_id=team_id,
            pattern_count=len(patterns),
            sequence_count=len(team_sequences),
            patterns=patterns
        )
