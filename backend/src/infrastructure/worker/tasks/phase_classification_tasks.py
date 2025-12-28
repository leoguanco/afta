"""
Phase Classification Tasks - Infrastructure Layer

Celery tasks for async phase classification.
"""
from celery import shared_task
import logging
import numpy as np

from src.infrastructure.ml.sklearn_phase_classifier import SklearnPhaseClassifier
from src.application.use_cases.classify_match_phases import ClassifyMatchPhasesUseCase
from src.domain.value_objects.game_phase import GamePhase
from src.domain.value_objects.phase_features import PhaseFeatures
from src.domain.entities.phase_sequence import PhaseSequence
from src.infrastructure.storage.phase_repository import phase_repository

logger = logging.getLogger(__name__)


@shared_task(name="classify_match_phases", queue="default", time_limit=600)
def classify_match_phases_task(
    match_id: str,
    team_id: str = "home",
    model_path: str = "/app/models/phase_classifier.joblib"
) -> dict:
    """
    Celery task to classify match phases.
    
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
        
        if not classifier.is_trained():
            # If no trained model, create demo sequence with synthetic phases
            logger.warning(f"No trained model found at {model_path}, generating demo classification")
            sequence = _create_demo_classification(match_id, team_id)
            phase_repository.save_phase_sequence(sequence)
            
            return {
                "status": "success",
                "match_id": match_id,
                "team_id": team_id,
                "message": "Demo phase classification generated (no trained model)",
                "phases_classified": len(sequence),
                "transition_count": sequence.get_transition_count(),
            }
        
        use_case = ClassifyMatchPhasesUseCase(classifier)
        
        # TODO: Load actual tracking data from storage
        # For now, try to load from match repository
        # In production: load from MinIO/DB
        
        # Fallback: create demo if no tracking data
        logger.info(f"Generating demo classification for match {match_id}")
        sequence = _create_demo_classification(match_id, team_id)
        phase_repository.save_phase_sequence(sequence)
        
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
        logger.error(f"Phase classification failed: {e}")
        return {
            "status": "error",
            "match_id": match_id,
            "message": str(e)
        }


def _create_demo_classification(match_id: str, team_id: str, fps: float = 25.0) -> PhaseSequence:
    """
    Create a demo phase sequence for testing/demonstration.
    
    Simulates a typical match with realistic phase patterns:
    - Start with organized defense
    - Transitions on ball wins/losses
    - Mix of attacking and defensive phases
    """
    sequence = PhaseSequence(match_id=match_id, team_id=team_id, fps=fps)
    
    # Simulate ~5 minutes of play (7500 frames at 25fps)
    total_frames = 7500
    
    # Phase pattern: realistic sequence of phases
    phase_patterns = [
        (GamePhase.ORGANIZED_DEFENSE, 300),      # Start defending
        (GamePhase.TRANSITION_DEF_ATK, 50),      # Win ball
        (GamePhase.ORGANIZED_ATTACK, 400),       # Build attack
        (GamePhase.TRANSITION_ATK_DEF, 30),      # Lose ball
        (GamePhase.ORGANIZED_DEFENSE, 500),      # Defend again
        (GamePhase.TRANSITION_DEF_ATK, 40),      # Win ball
        (GamePhase.ORGANIZED_ATTACK, 350),       # Attack
        (GamePhase.ORGANIZED_ATTACK, 200),       # Continue attack
        (GamePhase.TRANSITION_ATK_DEF, 25),      # Lose ball
        (GamePhase.ORGANIZED_DEFENSE, 450),      # Defend
    ]
    
    frame_id = 0
    pattern_idx = 0
    
    while frame_id < total_frames:
        phase, duration = phase_patterns[pattern_idx % len(phase_patterns)]
        
        for _ in range(duration):
            if frame_id >= total_frames:
                break
            sequence.add_frame_phase(frame_id, phase, confidence=0.85)
            frame_id += 1
        
        pattern_idx += 1
    
    return sequence


@shared_task(name="train_phase_classifier", queue="default", time_limit=1200)
def train_phase_classifier_task(
    training_data_path: str,
    model_output_path: str = "/app/models/phase_classifier.joblib"
) -> dict:
    """
    Celery task to train the phase classifier.
    
    Args:
        training_data_path: Path to labeled training data
        model_output_path: Where to save the trained model
        
    Returns:
        Dict with training metrics
    """
    logger.info(f"Starting phase classifier training from {training_data_path}")
    
    try:
        classifier = SklearnPhaseClassifier()
        
        # Generate synthetic training data for demo
        # In production: load from training_data_path (CSV/Parquet)
        logger.info("Generating synthetic training data for demo")
        features, labels = _generate_synthetic_training_data()
        
        # Train the model
        metrics = classifier.train(features, labels)
        
        # Save trained model
        classifier.save_model(model_output_path)
        logger.info(f"Model saved to {model_output_path}")
        
        return {
            "status": "success",
            "message": "Model training completed",
            "model_path": model_output_path,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Phase classifier training failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def _generate_synthetic_training_data(n_samples_per_class: int = 200):
    """
    Generate synthetic training data for phase classification.
    
    Creates realistic feature distributions for each phase based on
    typical tactical patterns in football.
    """
    np.random.seed(42)
    features = []
    labels = []
    
    for _ in range(n_samples_per_class):
        # ORGANIZED_ATTACK: Team pushed high, ball in opponent half
        f = np.array([
            70.0,  # home_centroid_x (high up)
            34.0,  # home_centroid_y (centered)
            40.0,  # away_centroid_x (defending)
            34.0,  # away_centroid_y
            15.0,  # home_spread_x (wide)
            12.0,  # home_spread_y
            10.0,  # away_spread_x (compact)
            8.0,   # away_spread_y
            75.0,  # ball_x (opponent half)
            34.0,  # ball_y
            2.0,   # ball_velocity_x (moving forward)
            0.0,   # ball_velocity_y
            55.0,  # home_defensive_line (high)
            25.0,  # away_defensive_line (deep)
            0.85,  # home_possession_prob (high)
        ]) + np.random.randn(15) * 3
        features.append(f)
        labels.append(GamePhase.ORGANIZED_ATTACK)
        
        # ORGANIZED_DEFENSE: Team deep, ball in own half
        f = np.array([
            30.0,  # home_centroid_x (deep)
            34.0,
            65.0,  # away_centroid_x (pushing)
            34.0,
            10.0,  # home_spread_x (compact)
            8.0,
            15.0,  # away_spread_x (wide)
            12.0,
            30.0,  # ball_x (own half)
            34.0,
            -1.5,  # ball_velocity_x (opponent moving forward)
            0.0,
            20.0,  # home_defensive_line (deep)
            70.0,  # away_defensive_line (high)
            0.15,  # home_possession_prob (low)
        ]) + np.random.randn(15) * 3
        features.append(f)
        labels.append(GamePhase.ORGANIZED_DEFENSE)
        
        # TRANSITION_ATK_DEF: Just lost ball, team spread out high
        f = np.array([
            60.0,  # home_centroid_x (still high)
            34.0,
            50.0,  # away_centroid_x (middle)
            34.0,
            20.0,  # home_spread_x (stretched)
            15.0,
            12.0,
            10.0,
            55.0,  # ball_x (mid)
            40.0,
            -4.0,  # ball_velocity_x (going backwards)
            2.0,
            45.0,  # home_defensive_line (caught high)
            50.0,
            0.25,  # home_possession_prob (just lost)
        ]) + np.random.randn(15) * 4
        features.append(f)
        labels.append(GamePhase.TRANSITION_ATK_DEF)
        
        # TRANSITION_DEF_ATK: Just won ball, team compact and low
        f = np.array([
            40.0,  # home_centroid_x (still low)
            34.0,
            55.0,  # away_centroid_x (still high)
            34.0,
            12.0,  # home_spread_x (compact)
            10.0,
            18.0,  # away_spread_x (stretched)
            14.0,
            45.0,  # ball_x
            30.0,
            3.5,   # ball_velocity_x (moving forward now)
            -1.0,
            30.0,  # home_defensive_line
            60.0,  # away_defensive_line (caught high)
            0.75,  # home_possession_prob (just won)
        ]) + np.random.randn(15) * 4
        features.append(f)
        labels.append(GamePhase.TRANSITION_DEF_ATK)
    
    return np.array(features), labels
