"""
PossessionSequence - Domain Layer

Rich Entity representing a ball possession sequence for pattern analysis.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.domain.value_objects.sequence_features import SequenceFeatures


@dataclass
class PossessionSequence:
    """
    Rich Entity: A continuous possession sequence by one team.
    
    A possession ends when:
    - Ball changes team (turnover)
    - Ball goes out of play
    - Goal is scored
    - Half ends
    """
    sequence_id: str
    match_id: str
    team_id: str
    
    # Frame range
    start_frame: int
    end_frame: int
    
    # Event indices
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    # Computed properties
    _features: Optional[SequenceFeatures] = field(default=None, repr=False)
    
    # Pattern assignment (set after clustering)
    pattern_id: Optional[str] = None
    cluster_label: Optional[int] = None
    
    def get_duration_seconds(self, fps: float = 25.0) -> float:
        """Calculate sequence duration in seconds."""
        frame_count = self.end_frame - self.start_frame
        return frame_count / fps
    
    def get_event_count(self) -> int:
        """Get number of events in sequence."""
        return len(self.events)
    
    def get_start_position(self) -> Optional[tuple]:
        """Get (x, y) position of first event."""
        if self.events:
            first = self.events[0]
            return (first.get('x', 0), first.get('y', 0))
        return None
    
    def get_end_position(self) -> Optional[tuple]:
        """Get (x, y) position of last event."""
        if self.events:
            last = self.events[-1]
            return (last.get('x', 0), last.get('y', 0))
        return None
    
    @staticmethod
    def _position_to_zone(x: float, y: float) -> int:
        """
        Convert pitch position to zone (1-12).
        
        Pitch divided into 4 horizontal x 3 vertical zones.
        Zone 1 = defensive left, Zone 12 = attacking right.
        """
        # x: 0-120 (StatsBomb), y: 0-80
        x_zone = min(3, int(x / 30))  # 0-3 (4 columns)
        y_zone = min(2, int(y / 27))  # 0-2 (3 rows)
        return x_zone * 3 + y_zone + 1
    
    def get_start_zone(self) -> int:
        """Get starting zone (1-12)."""
        pos = self.get_start_position()
        if pos:
            return self._position_to_zone(pos[0], pos[1])
        return 1
    
    def get_end_zone(self) -> int:
        """Get ending zone (1-12)."""
        pos = self.get_end_position()
        if pos:
            return self._position_to_zone(pos[0], pos[1])
        return 1
    
    def get_event_counts(self) -> Dict[str, int]:
        """Count events by type."""
        counts = {"pass": 0, "carry": 0, "dribble": 0, "shot": 0}
        for event in self.events:
            event_type = event.get("type", "").lower()
            if "pass" in event_type:
                counts["pass"] += 1
            elif "carry" in event_type:
                counts["carry"] += 1
            elif "dribble" in event_type:
                counts["dribble"] += 1
            elif "shot" in event_type:
                counts["shot"] += 1
        return counts
    
    def ended_in_shot(self) -> bool:
        """Check if sequence ended with a shot."""
        if self.events:
            last_type = self.events[-1].get("type", "").lower()
            return "shot" in last_type
        return False
    
    def ended_in_goal(self) -> bool:
        """Check if sequence resulted in a goal."""
        for event in reversed(self.events):
            if event.get("outcome", "").lower() == "goal":
                return True
        return False
    
    def extract_features(self, xt_grid: Optional[Any] = None) -> SequenceFeatures:
        """
        Extract feature vector for clustering.
        
        Args:
            xt_grid: Optional expected threat grid for xT values
        """
        if self._features is not None:
            return self._features
        
        event_counts = self.get_event_counts()
        
        # xT values (placeholder if no grid provided)
        xt_start = 0.01
        xt_end = 0.01
        
        if xt_grid is not None:
            start_pos = self.get_start_position()
            end_pos = self.get_end_position()
            if start_pos:
                xt_start = xt_grid.get_threat(start_pos[0], start_pos[1])
            if end_pos:
                xt_end = xt_grid.get_threat(end_pos[0], end_pos[1])
        
        features = SequenceFeatures(
            start_zone=self.get_start_zone(),
            end_zone=self.get_end_zone(),
            zone_progression=self.get_end_zone() - self.get_start_zone(),
            duration_seconds=self.get_duration_seconds(),
            event_count=self.get_event_count(),
            pass_count=event_counts["pass"],
            carry_count=event_counts["carry"],
            dribble_count=event_counts["dribble"],
            shot_attempted=event_counts["shot"] > 0,
            xt_start=xt_start,
            xt_end=xt_end,
            xt_progression=xt_end - xt_start,
            ended_in_shot=self.ended_in_shot(),
            ended_in_goal=self.ended_in_goal(),
            possession_lost=not self.ended_in_shot() and not self.ended_in_goal()
        )
        
        return features
