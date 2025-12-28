"""
ClassifyMatchPhasesUseCase - Application Layer

Orchestrates the classification of match frames into game phases.
"""
from typing import List, Optional
from dataclasses import dataclass

from src.domain.entities.phase_sequence import PhaseSequence, FramePhase
from src.domain.value_objects.game_phase import GamePhase
from src.domain.value_objects.phase_features import PhaseFeatures
from src.domain.ports.phase_classifier_port import PhaseClassifierPort


@dataclass
class ClassifyPhasesResult:
    """Result of phase classification."""
    match_id: str
    total_frames: int
    phases_classified: int
    phase_percentages: dict
    transition_count: int
    dominant_phase: GamePhase


class ClassifyMatchPhasesUseCase:
    """
    Use case for classifying match frames into game phases.
    
    This is the application layer orchestration that:
    1. Takes raw tracking data
    2. Extracts features per frame
    3. Runs ML classification
    4. Builds PhaseSequence entity
    """
    
    def __init__(self, classifier: PhaseClassifierPort):
        """
        Initialize with classifier.
        
        Args:
            classifier: PhaseClassifierPort implementation
        """
        self.classifier = classifier
    
    def execute(
        self,
        match_id: str,
        team_id: str,
        home_positions_per_frame: List[List[tuple]],
        away_positions_per_frame: List[List[tuple]],
        ball_positions: List[tuple],
        ball_velocities: Optional[List[tuple]] = None,
        fps: float = 25.0
    ) -> PhaseSequence:
        """
        Classify all frames in a match.
        
        Args:
            match_id: Match identifier
            team_id: Team perspective (home/away)
            home_positions_per_frame: List of home player positions per frame
            away_positions_per_frame: List of away player positions per frame
            ball_positions: Ball position per frame
            ball_velocities: Optional ball velocity per frame
            fps: Frames per second
            
        Returns:
            PhaseSequence with all frame classifications
        """
        if not self.classifier.is_trained():
            raise ValueError("Classifier is not trained")
        
        num_frames = len(ball_positions)
        if ball_velocities is None:
            ball_velocities = [(0.0, 0.0)] * num_frames
        
        # Extract features for all frames
        features_list = []
        for i in range(num_frames):
            home_pos = home_positions_per_frame[i] if i < len(home_positions_per_frame) else []
            away_pos = away_positions_per_frame[i] if i < len(away_positions_per_frame) else []
            ball_pos = ball_positions[i]
            ball_vel = ball_velocities[i] if i < len(ball_velocities) else (0.0, 0.0)
            
            features = PhaseFeatures.from_tracking_frame(
                home_positions=home_pos,
                away_positions=away_pos,
                ball_position=ball_pos,
                ball_velocity=ball_vel
            )
            features_list.append(features)
        
        # Classify in batch
        phases = self.classifier.classify_batch(features_list)
        
        # Build PhaseSequence
        sequence = PhaseSequence(
            match_id=match_id,
            team_id=team_id,
            fps=fps
        )
        
        for i, (phase, features) in enumerate(zip(phases, features_list)):
            sequence.add_frame_phase(
                frame_id=i,
                phase=phase,
                features=features
            )
        
        return sequence
    
    def execute_from_features(
        self,
        match_id: str,
        team_id: str,
        features_list: List[PhaseFeatures],
        fps: float = 25.0
    ) -> PhaseSequence:
        """
        Classify using pre-extracted features.
        
        Args:
            match_id: Match identifier
            team_id: Team perspective
            features_list: Pre-extracted features per frame
            fps: Frames per second
            
        Returns:
            PhaseSequence with all frame classifications
        """
        if not self.classifier.is_trained():
            raise ValueError("Classifier is not trained")
        
        # Classify with confidence
        sequence = PhaseSequence(
            match_id=match_id,
            team_id=team_id,
            fps=fps
        )
        
        for i, features in enumerate(features_list):
            phase, confidence = self.classifier.classify_with_confidence(features)
            sequence.add_frame_phase(
                frame_id=i,
                phase=phase,
                confidence=confidence,
                features=features
            )
        
        return sequence
    
    def get_summary(self, sequence: PhaseSequence) -> ClassifyPhasesResult:
        """Get summary statistics for a classified sequence."""
        return ClassifyPhasesResult(
            match_id=sequence.match_id,
            total_frames=len(sequence),
            phases_classified=len([fp for fp in sequence.frame_phases if fp.phase != GamePhase.UNKNOWN]),
            phase_percentages=sequence.get_phase_percentages(),
            transition_count=sequence.get_transition_count(),
            dominant_phase=sequence.get_dominant_phase()
        )
