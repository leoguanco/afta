"""
PhaseClassifier - Application Layer

Use Case for classifying match frames into game phases.
Follows strict Hexagonal Architecture rules.
"""
import logging
from typing import Optional, List, Tuple
import pandas as pd
import numpy as np

from src.domain.entities.phase_sequence import PhaseSequence
from src.domain.value_objects.phase_features import PhaseFeatures
from src.domain.ports.phase_classifier_port import PhaseClassifierPort
from src.domain.ports.phase_repository import PhaseRepository
from src.domain.ports.object_storage_port import ObjectStoragePort

logger = logging.getLogger(__name__)


class PhaseClassifier:
    """
    Use Case: Classify match phases.
    
    Orchestrates:
    1. Loading raw tracking data (Infra <-> Domain)
    2. Extracting features (Domain)
    3. Classification inference (Infra <-> Domain)
    4. Persisting results (Infra <-> Domain)
    """
    
    def __init__(
        self, 
        ml_engine: PhaseClassifierPort, 
        repository: PhaseRepository,
        object_storage: ObjectStoragePort
    ):
        """
        Initialize with injected dependencies.
        
        Args:
            ml_engine: ML Model adapter (PhaseClassifierPort)
            repository: Database adapter (PhaseRepository)
            object_storage: File storage adapter (ObjectStoragePort)
        """
        self.ml_engine = ml_engine
        self.repository = repository
        self.object_storage = object_storage
    
    def execute(self, match_id: str, team_id: str = "home") -> PhaseSequence:
        """
        Execute the phase classification use case.
        
        Args:
            match_id: Match identifier
            team_id: Team perspective
            
        Returns:
            Classified PhaseSequence entity
            
        Raises:
            ValueError: If tracking data missing or model issues
        """
        logger.info(f"Executing PhaseClassifier for match {match_id}")
        
        # 1. Load Tracking Data
        try:
            key = f"tracking/{match_id}.parquet"
            tracking_df = self.object_storage.get_parquet(key)
        except Exception as e:
            logger.error(f"Failed to load tracking data: {e}")
            raise ValueError(f"Tracking data not found for match {match_id}") from e
            
        if tracking_df.empty:
            raise ValueError(f"Tracking data is empty for match {match_id}")

        # 2. Extract Features & 3. Classify
        # Implementation note: We process frame-by-frame or batch here
        # This logic was previously in the Task, now moved to Application Layer
        
        if not self.ml_engine.is_trained():
             # In a strict environment, we might fail here.
             # Or we could trigger a separate "PhaseTrainer" use case.
             # For now, we assume requirements state it must be trained.
             raise ValueError("Phase classification model is not trained")

        sequence = self._process_classification(tracking_df, match_id, team_id)
        
        # 4. Save Results
        self.repository.save_phase_sequence(sequence)
        logger.info(f"Phase classification saved for {match_id}")
        
        return sequence

    def _process_classification(
        self, 
        df: pd.DataFrame, 
        match_id: str, 
        team_id: str
    ) -> PhaseSequence:
        """Internal helper to process dataframe into classified sequence."""
        sequence = PhaseSequence(match_id=match_id, team_id=team_id, fps=25.0)
        
        frame_ids = sorted(df['frame_id'].unique())
        batch_size = 500
        all_features = []
        
        # Feature Extraction Loop
        prev_ball_pos = (52.5, 34.0)
        
        for frame_id in frame_ids:
            # Extract positions (Domain helper could be used here if extracted to Utils)
            # For now, inline or private helper is fine to keep Use Case self-contained
            # or delegate to a Domain Service if complex.
            home_pos, away_pos, ball_pos = self._extract_positions(df, frame_id)
            
            ball_velocity = (
                (ball_pos[0] - prev_ball_pos[0]) * 25.0,
                (ball_pos[1] - prev_ball_pos[1]) * 25.0
            )
            prev_ball_pos = ball_pos
            
            features = PhaseFeatures.from_tracking_frame(
                home_positions=home_pos,
                away_positions=away_pos,
                ball_position=ball_pos,
                ball_velocity=ball_velocity
            )
            all_features.append((frame_id, features))
            
        # Classification Loop
        for i in range(0, len(all_features), batch_size):
            batch = all_features[i:i + batch_size]
            features_list = [f for _, f in batch]
            phases = self.ml_engine.classify_batch(features_list)
            
            for (frame_id, features), phase in zip(batch, phases):
                phase_with_conf, confidence = self.ml_engine.classify_with_confidence(features)
                sequence.add_frame_phase(
                    frame_id=frame_id,
                    phase=phase,
                    confidence=confidence
                )
        
        return sequence

    def _extract_positions(self, df: pd.DataFrame, frame_id: int) -> Tuple[List, List, Tuple]:
        """Helper to extract positions from dataframe row."""
        frame_data = df[df['frame_id'] == frame_id]
        if frame_data.empty:
            return [], [], (52.5, 34.0)
            
        home_data = frame_data[frame_data['team'] == 'home']
        away_data = frame_data[frame_data['team'] == 'away']
        
        home_pos = [(row['x'], row['y']) for _, row in home_data.iterrows()]
        away_pos = [(row['x'], row['y']) for _, row in away_data.iterrows()]
        
        ball_x = frame_data['ball_x'].iloc[0] if 'ball_x' in frame_data.columns else 52.5
        ball_y = frame_data['ball_y'].iloc[0] if 'ball_y' in frame_data.columns else 34.0
        
        return home_pos, away_pos, (ball_x, ball_y)
