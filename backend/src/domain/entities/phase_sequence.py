"""
PhaseSequence Entity - Domain Layer

Rich entity containing a sequence of game phases for a match.
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from src.domain.value_objects.game_phase import GamePhase
from src.domain.value_objects.phase_features import PhaseFeatures


@dataclass
class FramePhase:
    """Phase classification for a single frame."""
    frame_id: int
    phase: GamePhase
    confidence: float = 1.0
    features: Optional[PhaseFeatures] = None


@dataclass
class PhaseTransition:
    """Represents a transition between game phases."""
    frame_id: int
    from_phase: GamePhase
    to_phase: GamePhase
    timestamp: float = 0.0


@dataclass
class PhaseSequence:
    """
    Rich entity containing phase classifications for a match.
    
    This entity encapsulates the logic for:
    - Storing phase labels per frame
    - Detecting phase transitions
    - Calculating phase statistics
    """
    
    match_id: str
    team_id: str  # Which team's perspective (home/away)
    frame_phases: List[FramePhase] = field(default_factory=list)
    fps: float = 25.0
    
    def add_frame_phase(
        self, 
        frame_id: int, 
        phase: GamePhase, 
        confidence: float = 1.0,
        features: Optional[PhaseFeatures] = None
    ) -> None:
        """Add a phase classification for a frame."""
        self.frame_phases.append(FramePhase(
            frame_id=frame_id,
            phase=phase,
            confidence=confidence,
            features=features
        ))
        # Keep sorted by frame_id
        self.frame_phases.sort(key=lambda fp: fp.frame_id)
    
    def get_phase_at_frame(self, frame_id: int) -> GamePhase:
        """Get the phase at a specific frame."""
        for fp in self.frame_phases:
            if fp.frame_id == frame_id:
                return fp.phase
        return GamePhase.UNKNOWN
    
    def get_phases_in_range(self, start_frame: int, end_frame: int) -> List[FramePhase]:
        """Get all frame phases in a range."""
        return [
            fp for fp in self.frame_phases 
            if start_frame <= fp.frame_id <= end_frame
        ]
    
    def calculate_phase_transitions(self) -> List[PhaseTransition]:
        """
        Detect all phase transitions in the sequence.
        
        Returns:
            List of PhaseTransition objects
        """
        if len(self.frame_phases) < 2:
            return []
        
        transitions = []
        prev_phase = self.frame_phases[0].phase
        
        for fp in self.frame_phases[1:]:
            if fp.phase != prev_phase and fp.phase != GamePhase.UNKNOWN:
                transitions.append(PhaseTransition(
                    frame_id=fp.frame_id,
                    from_phase=prev_phase,
                    to_phase=fp.phase,
                    timestamp=fp.frame_id / self.fps
                ))
                prev_phase = fp.phase
        
        return transitions
    
    def get_phase_durations(self) -> dict[GamePhase, float]:
        """
        Calculate total duration spent in each phase.
        
        Returns:
            Dict mapping GamePhase to seconds
        """
        durations: dict[GamePhase, float] = {phase: 0.0 for phase in GamePhase}
        
        if not self.frame_phases:
            return durations
        
        for i in range(len(self.frame_phases) - 1):
            current = self.frame_phases[i]
            next_frame = self.frame_phases[i + 1]
            frame_duration = (next_frame.frame_id - current.frame_id) / self.fps
            durations[current.phase] += frame_duration
        
        # Add last frame duration (assume 1 frame)
        if self.frame_phases:
            durations[self.frame_phases[-1].phase] += 1.0 / self.fps
        
        return durations
    
    def get_phase_percentages(self) -> dict[GamePhase, float]:
        """
        Calculate percentage of time spent in each phase.
        
        Returns:
            Dict mapping GamePhase to percentage (0-100)
        """
        durations = self.get_phase_durations()
        total = sum(durations.values())
        
        if total == 0:
            return {phase: 0.0 for phase in GamePhase}
        
        return {
            phase: (duration / total) * 100 
            for phase, duration in durations.items()
        }
    
    def get_dominant_phase(self) -> GamePhase:
        """Get the phase with the most time."""
        durations = self.get_phase_durations()
        # Exclude UNKNOWN
        valid_durations = {
            k: v for k, v in durations.items() 
            if k != GamePhase.UNKNOWN
        }
        if not valid_durations or max(valid_durations.values()) == 0:
            return GamePhase.UNKNOWN
        return max(valid_durations, key=valid_durations.get)
    
    def get_transition_count(self) -> int:
        """Count total number of phase transitions."""
        return len(self.calculate_phase_transitions())
    
    def __len__(self) -> int:
        return len(self.frame_phases)
    
    def __repr__(self) -> str:
        return f"PhaseSequence(match={self.match_id}, frames={len(self)})"
