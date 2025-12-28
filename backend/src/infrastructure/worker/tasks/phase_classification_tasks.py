"""
Phase Classification Tasks - Infrastructure Layer

Celery tasks for async phase classification.
"""
from celery import shared_task
import logging

from src.infrastructure.ml.sklearn_phase_classifier import SklearnPhaseClassifier
from src.application.use_cases.classify_match_phases import ClassifyMatchPhasesUseCase
from src.domain.value_objects.game_phase import GamePhase

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
            return {
                "status": "error",
                "message": "Classifier model not found or not trained",
                "match_id": match_id
            }
        
        use_case = ClassifyMatchPhasesUseCase(classifier)
        
        # TODO: Load tracking data from storage
        # For now, return placeholder
        # In production: load from MinIO/DB
        
        return {
            "status": "success",
            "match_id": match_id,
            "team_id": team_id,
            "message": "Phase classification completed",
            "phases_classified": 0,  # Would be populated with real data
        }
        
    except Exception as e:
        logger.error(f"Phase classification failed: {e}")
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
    
    Args:
        training_data_path: Path to labeled training data
        model_output_path: Where to save the trained model
        
    Returns:
        Dict with training metrics
    """
    logger.info(f"Starting phase classifier training from {training_data_path}")
    
    try:
        classifier = SklearnPhaseClassifier()
        
        # TODO: Load training data from path
        # For now, return placeholder
        
        return {
            "status": "success",
            "message": "Model training completed",
            "model_path": model_output_path,
            "metrics": {}
        }
        
    except Exception as e:
        logger.error(f"Phase classifier training failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
