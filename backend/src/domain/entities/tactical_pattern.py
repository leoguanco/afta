"""
TacticalPattern - Domain Layer

Rich Entity representing a discovered tactical pattern from clustering.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class TacticalPattern:
    """
    Rich Entity: A discovered tactical pattern.
    
    Represents a cluster of similar possession sequences.
    """
    pattern_id: str
    match_id: str
    team_id: str
    
    # Cluster info
    cluster_label: int
    
    # Human-readable label (assigned by labeler)
    label: str = "Unknown Pattern"
    description: Optional[str] = None
    
    # Statistics
    occurrence_count: int = 0
    success_count: int = 0  # Ended in shot or goal
    goal_count: int = 0
    
    # Aggregated metrics
    avg_duration_seconds: float = 0.0
    avg_event_count: float = 0.0
    avg_xt_progression: float = 0.0
    
    # Representative sequence IDs
    example_sequences: List[str] = field(default_factory=list)
    
    # Cluster centroid (feature space)
    centroid: Optional[List[float]] = None
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate (shots or goals)."""
        if self.occurrence_count == 0:
            return 0.0
        return self.success_count / self.occurrence_count
    
    @property
    def goal_rate(self) -> float:
        """Calculate goal conversion rate."""
        if self.occurrence_count == 0:
            return 0.0
        return self.goal_count / self.occurrence_count
    
    def add_sequence(
        self,
        sequence_id: str,
        ended_in_shot: bool,
        ended_in_goal: bool,
        duration: float,
        event_count: int,
        xt_progression: float
    ) -> None:
        """Add a sequence to this pattern's statistics."""
        # Update counts
        self.occurrence_count += 1
        if ended_in_shot or ended_in_goal:
            self.success_count += 1
        if ended_in_goal:
            self.goal_count += 1
        
        # Update running averages
        n = self.occurrence_count
        self.avg_duration_seconds = (
            (self.avg_duration_seconds * (n - 1) + duration) / n
        )
        self.avg_event_count = (
            (self.avg_event_count * (n - 1) + event_count) / n
        )
        self.avg_xt_progression = (
            (self.avg_xt_progression * (n - 1) + xt_progression) / n
        )
        
        # Store example sequences (up to 5)
        if len(self.example_sequences) < 5:
            self.example_sequences.append(sequence_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "pattern_id": self.pattern_id,
            "match_id": self.match_id,
            "team_id": self.team_id,
            "cluster_label": self.cluster_label,
            "label": self.label,
            "description": self.description,
            "occurrence_count": self.occurrence_count,
            "success_rate": round(self.success_rate, 3),
            "goal_rate": round(self.goal_rate, 3),
            "avg_duration_seconds": round(self.avg_duration_seconds, 2),
            "avg_event_count": round(self.avg_event_count, 1),
            "avg_xt_progression": round(self.avg_xt_progression, 4),
            "example_sequences": self.example_sequences
        }
