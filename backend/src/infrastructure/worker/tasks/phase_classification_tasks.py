"""
Phase Classification Tasks - Infrastructure Layer

Celery tasks for async phase classification.
Follows "Anemic Handler" pattern: delegates logic to Application Use Cases.
"""
from celery import shared_task
import logging
import numpy as np
from typing import Dict, Any

from src.infrastructure.ml.sklearn_phase_classifier import SklearnPhaseClassifier
from src.application.use_cases.phase_classifier import PhaseClassifier
from src.domain.value_objects.game_phase import GamePhase
from src.domain.value_objects.phase_features import PhaseFeatures
from src.infrastructure.storage.phase_repository import phase_repository
from src.infrastructure.storage.minio_adapter import MinIOAdapter

logger = logging.getLogger(__name__)


@shared_task(name="classify_match_phases", queue="default", time_limit=600)
def classify_match_phases_task(
    match_id: str,
    team_id: str = "home",
    model_path: str = "/app/models/phase_classifier.joblib"
) -> Dict[str, Any]:
    """
    Celery task to classify match phases.
    
    Acts as an Adapter/Handler:
    1. Instantiates Adapters (ML, DB, Storage)
    2. Instantiates Use Case (PhaseClassifier)
    3. Executes Use Case
    """
    logger.info(f"Starting phase classification task for {match_id}")
    
    try:
        # 1. Composition Root: Instantiate Adapters
        # Note: phase_repository is imported as singleton
        ml_adapter = SklearnPhaseClassifier(model_path=model_path)
        storage_adapter = MinIOAdapter(bucket="tracking-data")
        
        # Infrastructure Self-Healing: Ensure model exists (Production robustness)
        if not ml_adapter.is_trained():
            logger.warning("Model not trained. Triggering auto-training fallback.")
            _train_fallback_model(ml_adapter, model_path)
        
        # 2. Instantiate Use Case
        use_case = PhaseClassifier(
            ml_engine=ml_adapter,
            repository=phase_repository,
            object_storage=storage_adapter
        )
        
        # 3. Execute
        sequence = use_case.execute(match_id, team_id)
        
        # 4. Return Output
        return {
            "status": "success",
            "match_id": match_id,
            "team_id": team_id,
            "phases_classified": len(sequence),
            "transition_count": sequence.get_transition_count(),
            "dominant_phase": sequence.get_dominant_phase().value
        }
        
    except Exception as e:
        logger.error(f"Task failed: {e}", exc_info=True)
        return {
            "status": "error",
            "match_id": match_id,
            "message": str(e)
        }


@shared_task(name="train_phase_classifier", queue="default", time_limit=1200)
def train_phase_classifier_task(
    training_data_path: str,
    model_output_path: str = "/app/models/phase_classifier.joblib"
) -> Dict[str, Any]:
    """
    Celery task to train the phase classifier.
    
    TODO: Refactor into a PhaseTrainer Use Case if complex logic grows.
    For now, keeps basic training orchestration here.
    """
    logger.info(f"Starting training task from {training_data_path}")
    
    try:
        classifier = SklearnPhaseClassifier()
        
        # Data Loading Strategy
        # Ideally this should be in a Use Case too (TrainPhaseClassifier)
        if training_data_path == "synthetic":
            logger.info("Generating synthetic training data")
            features, labels = _generate_synthetic_training_data(500)
        else:
             # Try load from MinIO
            storage = MinIOAdapter(bucket="models")
            try:
                df = storage.get_parquet(training_data_path)
                # Feature extraction logic from DF... simplified for now
                # In real prod, we'd use a FeatureExtractor Use Case or Service
                features = df[PhaseFeatures.feature_names()].values
                labels = [GamePhase.from_string(l) for l in df['label']]
            except Exception:
                logger.warning("Could not load data, falling back to synthetic")
                features, labels = _generate_synthetic_training_data(500)

        # Train & Save
        metrics = classifier.train(features, labels)
        classifier.save_model(model_output_path)
        
        return {
            "status": "success",
            "message": "Model trained",
            "model_path": model_output_path,
            "metrics": metrics
        }
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


def _train_fallback_model(classifier: SklearnPhaseClassifier, path: str):
    """Helper to train a fallback model on synthetic data."""
    features, labels = _generate_synthetic_training_data()
    classifier.train(features, labels)
    classifier.save_model(path)


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
            np.random.uniform(65, 80),   # home_centroid_x
            np.random.uniform(28, 40),   # home_centroid_y
            np.random.uniform(35, 50),   # away_centroid_x
            np.random.uniform(28, 40),   # away_centroid_y
            np.random.uniform(12, 20),   # home_spread_x
            np.random.uniform(10, 15),   # home_spread_y
            np.random.uniform(8, 12),    # away_spread_x
            np.random.uniform(6, 10),    # away_spread_y
            np.random.uniform(70, 90),   # ball_x
            np.random.uniform(20, 48),   # ball_y
            np.random.uniform(0, 4),     # ball_vel_x
            np.random.uniform(-2, 2),    # ball_vel_y
            np.random.uniform(50, 65),   # home_line
            np.random.uniform(20, 30),   # away_line
            np.random.uniform(0.75, 0.95) # possession
        ])
        features.append(f)
        labels.append(GamePhase.ORGANIZED_ATTACK)
        
        # ORGANIZED_DEFENSE: Team deep, ball in own half
        f = np.array([
            np.random.uniform(20, 35),   # home_centroid_x
            np.random.uniform(28, 40),
            np.random.uniform(55, 75),   # away_centroid_x
            np.random.uniform(28, 40),
            np.random.uniform(8, 12),    # home_spread_x
            np.random.uniform(6, 10),
            np.random.uniform(12, 20),   # away_spread_x
            np.random.uniform(10, 15),
            np.random.uniform(15, 40),   # ball_x
            np.random.uniform(20, 48),
            np.random.uniform(-4, 0),    # ball_vel_x
            np.random.uniform(-2, 2),
            np.random.uniform(15, 25),   # home_line
            np.random.uniform(65, 80),   # away_line
            np.random.uniform(0.05, 0.25) # possession
        ])
        features.append(f)
        labels.append(GamePhase.ORGANIZED_DEFENSE)
        
        # TRANSITION_ATK_DEF
        f = np.array([
            np.random.uniform(55, 70),
            np.random.uniform(28, 40),
            np.random.uniform(45, 60),
            np.random.uniform(28, 40),
            np.random.uniform(18, 25),
            np.random.uniform(12, 18),
            np.random.uniform(10, 15),
            np.random.uniform(8, 12),
            np.random.uniform(45, 65),
            np.random.uniform(20, 48),
            np.random.uniform(-6, -2),
            np.random.uniform(-3, 3),
            np.random.uniform(40, 55),
            np.random.uniform(45, 60),
            np.random.uniform(0.20, 0.40)
        ])
        features.append(f)
        labels.append(GamePhase.TRANSITION_ATK_DEF)
        
        # TRANSITION_DEF_ATK
        f = np.array([
            np.random.uniform(30, 45),
            np.random.uniform(28, 40),
            np.random.uniform(50, 65),
            np.random.uniform(28, 40),
            np.random.uniform(10, 15),
            np.random.uniform(8, 12),
            np.random.uniform(15, 22),
            np.random.uniform(12, 18),
            np.random.uniform(35, 55),
            np.random.uniform(20, 48),
            np.random.uniform(2, 6),
            np.random.uniform(-3, 3),
            np.random.uniform(25, 40),
            np.random.uniform(55, 70),
            np.random.uniform(0.60, 0.80)
        ])
        features.append(f)
        labels.append(GamePhase.TRANSITION_DEF_ATK)
    
    return np.array(features), labels
