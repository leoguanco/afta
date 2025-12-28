"""
Phase Classification Tasks - Infrastructure Layer

Celery tasks for async phase classification.
Full production implementation with MinIO tracking data integration.
"""
from celery import shared_task
import logging
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional

from src.infrastructure.ml.sklearn_phase_classifier import SklearnPhaseClassifier
from src.application.use_cases.classify_match_phases import ClassifyMatchPhasesUseCase
from src.domain.value_objects.game_phase import GamePhase
from src.domain.value_objects.phase_features import PhaseFeatures
from src.domain.entities.phase_sequence import PhaseSequence
from src.infrastructure.storage.phase_repository import phase_repository
from src.infrastructure.storage.minio_adapter import MinIOAdapter

logger = logging.getLogger(__name__)


def _load_tracking_data_from_minio(match_id: str) -> Optional[pd.DataFrame]:
    """
    Load tracking data from MinIO object storage.
    
    Expected parquet format:
    - frame_id: int
    - team: str ('home' or 'away')
    - player_id: int/str
    - x: float (pitch coordinates 0-105m)
    - y: float (pitch coordinates 0-68m)
    - ball_x: float (ball position, same for all rows in frame)
    - ball_y: float
    
    Args:
        match_id: Match identifier
        
    Returns:
        DataFrame with tracking data or None if not found
    """
    try:
        storage = MinIOAdapter(bucket="tracking-data")
        key = f"tracking/{match_id}.parquet"
        df = storage.get_parquet(key)
        logger.info(f"Loaded tracking data for match {match_id}: {len(df)} rows")
        return df
    except Exception as e:
        logger.warning(f"Could not load tracking data from MinIO for {match_id}: {e}")
        return None


def _extract_positions_from_dataframe(
    df: pd.DataFrame, 
    frame_id: int
) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]], Tuple[float, float]]:
    """
    Extract home/away positions and ball position for a single frame.
    
    Args:
        df: Full tracking DataFrame
        frame_id: Frame to extract
        
    Returns:
        Tuple of (home_positions, away_positions, ball_position)
    """
    frame_data = df[df['frame_id'] == frame_id]
    
    if frame_data.empty:
        return [], [], (52.5, 34.0)  # Default to center
    
    home_data = frame_data[frame_data['team'] == 'home']
    away_data = frame_data[frame_data['team'] == 'away']
    
    home_positions = [(row['x'], row['y']) for _, row in home_data.iterrows()]
    away_positions = [(row['x'], row['y']) for _, row in away_data.iterrows()]
    
    # Ball position (take from first row, should be same for all in frame)
    ball_x = frame_data['ball_x'].iloc[0] if 'ball_x' in frame_data.columns else 52.5
    ball_y = frame_data['ball_y'].iloc[0] if 'ball_y' in frame_data.columns else 34.0
    
    return home_positions, away_positions, (ball_x, ball_y)


def _classify_from_tracking_data(
    classifier: SklearnPhaseClassifier,
    df: pd.DataFrame,
    match_id: str,
    team_id: str,
    fps: float = 25.0
) -> PhaseSequence:
    """
    Run classification on actual tracking data.
    
    Args:
        classifier: Trained classifier
        df: Tracking data DataFrame
        match_id: Match identifier
        team_id: Team perspective
        fps: Frames per second
        
    Returns:
        PhaseSequence with classifications
    """
    sequence = PhaseSequence(match_id=match_id, team_id=team_id, fps=fps)
    
    # Get unique frame IDs sorted
    frame_ids = sorted(df['frame_id'].unique())
    
    # Extract features and classify in batches for efficiency
    batch_size = 500
    all_features = []
    
    prev_ball_pos = (52.5, 34.0)
    
    for frame_id in frame_ids:
        home_pos, away_pos, ball_pos = _extract_positions_from_dataframe(df, frame_id)
        
        # Calculate ball velocity from previous frame
        ball_velocity = (
            (ball_pos[0] - prev_ball_pos[0]) * fps,
            (ball_pos[1] - prev_ball_pos[1]) * fps
        )
        prev_ball_pos = ball_pos
        
        features = PhaseFeatures.from_tracking_frame(
            home_positions=home_pos,
            away_positions=away_pos,
            ball_position=ball_pos,
            ball_velocity=ball_velocity
        )
        all_features.append((frame_id, features))
    
    # Classify in batches
    for i in range(0, len(all_features), batch_size):
        batch = all_features[i:i + batch_size]
        features_list = [f for _, f in batch]
        phases = classifier.classify_batch(features_list)
        
        for (frame_id, features), phase in zip(batch, phases):
            phase_with_conf, confidence = classifier.classify_with_confidence(features)
            sequence.add_frame_phase(
                frame_id=frame_id,
                phase=phase,
                confidence=confidence
            )
    
    return sequence


@shared_task(name="classify_match_phases", queue="default", time_limit=600)
def classify_match_phases_task(
    match_id: str,
    team_id: str = "home",
    model_path: str = "/app/models/phase_classifier.joblib"
) -> dict:
    """
    Celery task to classify match phases.
    
    Loads tracking data from MinIO, extracts features, and runs
    ML classification to label each frame with a game phase.
    Results are stored in PostgreSQL.
    
    Args:
        match_id: Match identifier
        team_id: Team perspective (home/away)
        model_path: Path to trained model
        
    Returns:
        Dict with classification results
    """
    logger.info(f"Starting phase classification for match {match_id}")
    
    try:
        # Load classifier
        classifier = SklearnPhaseClassifier(model_path=model_path)
        
        # Load tracking data from MinIO
        tracking_df = _load_tracking_data_from_minio(match_id)
        
        if tracking_df is None or tracking_df.empty:
            logger.warning(f"No tracking data found for match {match_id}")
            return {
                "status": "error",
                "match_id": match_id,
                "message": "No tracking data found in MinIO. Upload tracking data first."
            }
        
        # If no trained model, train on synthetic data first
        if not classifier.is_trained():
            logger.info("No trained model found, training on synthetic data...")
            features, labels = _generate_synthetic_training_data()
            metrics = classifier.train(features, labels)
            classifier.save_model(model_path)
            logger.info(f"Model trained and saved: accuracy={metrics['accuracy']:.3f}")
        
        # Run classification
        sequence = _classify_from_tracking_data(
            classifier=classifier,
            df=tracking_df,
            match_id=match_id,
            team_id=team_id
        )
        
        # Save to PostgreSQL
        phase_repository.save_phase_sequence(sequence)
        logger.info(f"Saved phase sequence to database: {len(sequence)} frames")
        
        return {
            "status": "success",
            "match_id": match_id,
            "team_id": team_id,
            "message": "Phase classification completed",
            "phases_classified": len(sequence),
            "transition_count": sequence.get_transition_count(),
            "phase_percentages": {
                phase.value: pct 
                for phase, pct in sequence.get_phase_percentages().items()
            }
        }
        
    except Exception as e:
        logger.error(f"Phase classification failed: {e}", exc_info=True)
        return {
            "status": "error",
            "match_id": match_id,
            "message": str(e)
        }


@shared_task(name="train_phase_classifier", queue="default", time_limit=1200)
def train_phase_classifier_task(
    training_data_path: str,
    model_output_path: str = "/app/models/phase_classifier.joblib"
) -> dict:
    """
    Celery task to train the phase classifier.
    
    If training_data_path points to a valid parquet file in MinIO,
    loads and uses that data. Otherwise, generates synthetic training
    data based on tactical patterns.
    
    Args:
        training_data_path: Path to labeled training data (MinIO key)
        model_output_path: Where to save the trained model
        
    Returns:
        Dict with training metrics
    """
    logger.info(f"Starting phase classifier training from {training_data_path}")
    
    try:
        classifier = SklearnPhaseClassifier()
        
        # Try to load training data from MinIO
        training_data = _load_training_data(training_data_path)
        
        if training_data is not None:
            features, labels = training_data
            logger.info(f"Loaded {len(labels)} training samples from {training_data_path}")
        else:
            # Generate synthetic training data
            logger.info("Generating synthetic training data based on tactical patterns")
            features, labels = _generate_synthetic_training_data(n_samples_per_class=500)
        
        # Train the model
        metrics = classifier.train(features, labels)
        
        # Save trained model
        classifier.save_model(model_output_path)
        logger.info(f"Model saved to {model_output_path}")
        
        return {
            "status": "success",
            "message": "Model training completed",
            "model_path": model_output_path,
            "metrics": {
                "accuracy": metrics['accuracy'],
                "accuracy_std": metrics.get('accuracy_std', 0),
                "n_samples": metrics['n_samples'],
                "n_features": metrics['n_features'],
            },
            "feature_importances": metrics.get('feature_importances', {})
        }
        
    except Exception as e:
        logger.error(f"Phase classifier training failed: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }


def _load_training_data(path: str) -> Optional[Tuple[np.ndarray, List[GamePhase]]]:
    """
    Load labeled training data from MinIO.
    
    Expected format: Parquet with columns matching PhaseFeatures
    plus a 'label' column with phase string values.
    
    Args:
        path: MinIO object key
        
    Returns:
        Tuple of (features array, labels list) or None
    """
    try:
        storage = MinIOAdapter(bucket="models")
        df = storage.get_parquet(path)
        
        # Extract features and labels
        feature_cols = PhaseFeatures.feature_names()
        if not all(col in df.columns for col in feature_cols):
            logger.warning(f"Training data missing required columns")
            return None
        
        features = df[feature_cols].values
        labels = [GamePhase.from_string(label) for label in df['label']]
        
        return features, labels
        
    except Exception as e:
        logger.warning(f"Could not load training data from {path}: {e}")
        return None


def _generate_synthetic_training_data(n_samples_per_class: int = 200):
    """
    Generate synthetic training data for phase classification.
    
    Creates realistic feature distributions for each phase based on
    typical tactical patterns in football. Uses domain knowledge
    about team positioning during each phase.
    
    Args:
        n_samples_per_class: Number of samples per phase
        
    Returns:
        Tuple of (features array, labels list)
    """
    np.random.seed(42)
    features = []
    labels = []
    
    for _ in range(n_samples_per_class):
        # ORGANIZED_ATTACK: Team pushed high, ball in opponent half
        # Typical scenario: maintaining possession in final third
        f = np.array([
            np.random.uniform(65, 80),   # home_centroid_x (high up)
            np.random.uniform(28, 40),   # home_centroid_y (centered)
            np.random.uniform(35, 50),   # away_centroid_x (defending deep)
            np.random.uniform(28, 40),   # away_centroid_y
            np.random.uniform(12, 20),   # home_spread_x (wide in attack)
            np.random.uniform(10, 15),   # home_spread_y
            np.random.uniform(8, 12),    # away_spread_x (compact defense)
            np.random.uniform(6, 10),    # away_spread_y
            np.random.uniform(70, 90),   # ball_x (opponent half)
            np.random.uniform(20, 48),   # ball_y
            np.random.uniform(0, 4),     # ball_velocity_x (moving forward)
            np.random.uniform(-2, 2),    # ball_velocity_y
            np.random.uniform(50, 65),   # home_defensive_line (high)
            np.random.uniform(20, 30),   # away_defensive_line (deep)
            np.random.uniform(0.75, 0.95),  # home_possession_prob (high)
        ])
        features.append(f)
        labels.append(GamePhase.ORGANIZED_ATTACK)
        
        # ORGANIZED_DEFENSE: Team deep, ball in own half
        # Typical scenario: defending against opponent pressure
        f = np.array([
            np.random.uniform(20, 35),   # home_centroid_x (deep)
            np.random.uniform(28, 40),   # home_centroid_y
            np.random.uniform(55, 75),   # away_centroid_x (pushing high)
            np.random.uniform(28, 40),   # away_centroid_y
            np.random.uniform(8, 12),    # home_spread_x (compact)
            np.random.uniform(6, 10),    # home_spread_y
            np.random.uniform(12, 20),   # away_spread_x (wide attack)
            np.random.uniform(10, 15),   # away_spread_y
            np.random.uniform(15, 40),   # ball_x (own half)
            np.random.uniform(20, 48),   # ball_y
            np.random.uniform(-4, 0),    # ball_velocity_x (opponent moving forward)
            np.random.uniform(-2, 2),    # ball_velocity_y
            np.random.uniform(15, 25),   # home_defensive_line (deep)
            np.random.uniform(65, 80),   # away_defensive_line (high press)
            np.random.uniform(0.05, 0.25),  # home_possession_prob (low)
        ])
        features.append(f)
        labels.append(GamePhase.ORGANIZED_DEFENSE)
        
        # TRANSITION_ATK_DEF: Just lost ball, team stretched high
        # Typical scenario: turnover in attacking third, counter-press needed
        f = np.array([
            np.random.uniform(55, 70),   # home_centroid_x (still high from attack)
            np.random.uniform(28, 40),   # home_centroid_y
            np.random.uniform(45, 60),   # away_centroid_x (middle, launching counter)
            np.random.uniform(28, 40),   # away_centroid_y
            np.random.uniform(18, 25),   # home_spread_x (stretched)
            np.random.uniform(12, 18),   # home_spread_y (disorganized)
            np.random.uniform(10, 15),   # away_spread_x
            np.random.uniform(8, 12),    # away_spread_y
            np.random.uniform(45, 65),   # ball_x (middle, moving back)
            np.random.uniform(20, 48),   # ball_y
            np.random.uniform(-6, -2),   # ball_velocity_x (going backwards fast)
            np.random.uniform(-3, 3),    # ball_velocity_y (diagonal runs)
            np.random.uniform(40, 55),   # home_defensive_line (caught high)
            np.random.uniform(45, 60),   # away_defensive_line
            np.random.uniform(0.20, 0.40),  # home_possession_prob (just lost)
        ])
        features.append(f)
        labels.append(GamePhase.TRANSITION_ATK_DEF)
        
        # TRANSITION_DEF_ATK: Just won ball, team compact and low
        # Typical scenario: regain in own half, looking to spring counter
        f = np.array([
            np.random.uniform(30, 45),   # home_centroid_x (still low)
            np.random.uniform(28, 40),   # home_centroid_y
            np.random.uniform(50, 65),   # away_centroid_x (still pushing)
            np.random.uniform(28, 40),   # away_centroid_y
            np.random.uniform(10, 15),   # home_spread_x (compact from defense)
            np.random.uniform(8, 12),    # home_spread_y
            np.random.uniform(15, 22),   # away_spread_x (stretched from attack)
            np.random.uniform(12, 18),   # away_spread_y (disorganized)
            np.random.uniform(35, 55),   # ball_x (won in own/middle)
            np.random.uniform(20, 48),   # ball_y
            np.random.uniform(2, 6),     # ball_velocity_x (now moving forward)
            np.random.uniform(-3, 3),    # ball_velocity_y
            np.random.uniform(25, 40),   # home_defensive_line
            np.random.uniform(55, 70),   # away_defensive_line (caught high)
            np.random.uniform(0.60, 0.80),  # home_possession_prob (just won)
        ])
        features.append(f)
        labels.append(GamePhase.TRANSITION_DEF_ATK)
    
    return np.array(features), labels
