"""
SequenceFeatures - Domain Layer

Value Object representing features extracted from a possession sequence for ML clustering.
"""
from dataclasses import dataclass
from typing import List, Optional
import numpy as np


@dataclass(frozen=True)
class SequenceFeatures:
    """
    Value Object: Feature vector for a possession sequence.
    
    Used as input for pattern detection clustering algorithms.
    """
    # Spatial features
    start_zone: int  # 1-12 (pitch divided into 12 zones)
    end_zone: int
    zone_progression: int  # end_zone - start_zone (positive = forward)
    
    # Temporal features
    duration_seconds: float
    event_count: int
    
    # Event composition
    pass_count: int
    carry_count: int
    dribble_count: int
    shot_attempted: bool
    
    # Quality metrics
    xt_start: float  # Expected threat at start
    xt_end: float    # Expected threat at end
    xt_progression: float  # xt_end - xt_start
    
    # Outcome
    ended_in_shot: bool
    ended_in_goal: bool
    possession_lost: bool
    
    def to_vector(self) -> np.ndarray:
        """Convert to numpy array for ML algorithms."""
        return np.array([
            self.start_zone,
            self.end_zone,
            self.zone_progression,
            self.duration_seconds,
            self.event_count,
            self.pass_count,
            self.carry_count,
            self.dribble_count,
            1.0 if self.shot_attempted else 0.0,
            self.xt_start,
            self.xt_end,
            self.xt_progression,
            1.0 if self.ended_in_shot else 0.0,
            1.0 if self.ended_in_goal else 0.0,
            1.0 if self.possession_lost else 0.0
        ], dtype=np.float32)
    
    @staticmethod
    def feature_names() -> List[str]:
        """Return list of feature names for interpretability."""
        return [
            "start_zone", "end_zone", "zone_progression",
            "duration_seconds", "event_count",
            "pass_count", "carry_count", "dribble_count", "shot_attempted",
            "xt_start", "xt_end", "xt_progression",
            "ended_in_shot", "ended_in_goal", "possession_lost"
        ]
    
    @staticmethod
    def from_vector(vec: np.ndarray) -> "SequenceFeatures":
        """Create from numpy array."""
        return SequenceFeatures(
            start_zone=int(vec[0]),
            end_zone=int(vec[1]),
            zone_progression=int(vec[2]),
            duration_seconds=float(vec[3]),
            event_count=int(vec[4]),
            pass_count=int(vec[5]),
            carry_count=int(vec[6]),
            dribble_count=int(vec[7]),
            shot_attempted=bool(vec[8] > 0.5),
            xt_start=float(vec[9]),
            xt_end=float(vec[10]),
            xt_progression=float(vec[11]),
            ended_in_shot=bool(vec[12] > 0.5),
            ended_in_goal=bool(vec[13] > 0.5),
            possession_lost=bool(vec[14] > 0.5)
        )
