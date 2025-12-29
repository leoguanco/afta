"""
Phase Classification API Endpoints - Infrastructure Layer

Endpoints for game phase classification and querying.
"""
from fastapi import APIRouter
from pydantic import BaseModel

from src.infrastructure.worker.celery_app import celery_app

router = APIRouter(prefix="/api/v1", tags=["phases"])


class PhaseClassificationRequest(BaseModel):
    """Request body for phase classification endpoint."""
    match_id: str
    team_id: str = "home"  # Perspective: home or away


class TrainClassifierRequest(BaseModel):
    """Request body for classifier training."""
    training_data_path: str
    model_name: str = "phase_classifier"


@router.post("/matches/{match_id}/classify-phases")
async def classify_match_phases(match_id: str, request: PhaseClassificationRequest = None):
    """
    Start an async phase classification job.
    
    Classifies each frame of tracking data into one of 4 game phases:
    - ORGANIZED_ATTACK
    - ORGANIZED_DEFENSE
    - TRANSITION_ATK_DEF
    - TRANSITION_DEF_ATK
    
    Requires a trained ML model to be available.
    
    Returns immediately with a job_id for status polling.
    """
    team_id = request.team_id if request else "home"
    
    task = celery_app.send_task(
        'classify_match_phases',  # Uses shared_task name
        args=[match_id, team_id]
    )
    
    return {
        "job_id": task.id,
        "status": "PENDING",
        "message": f"Phase classification started for match {match_id}",
    }


@router.get("/matches/{match_id}/phases")
async def get_match_phases(
    match_id: str,
    start_frame: int = 0,
    end_frame: int = None,
    team_id: str = "home"
):
    """
    Get classified phases for a match.
    
    Returns phase labels, transitions, and statistics for the specified frame range.
    
    Query params:
    - start_frame: First frame to include (default: 0)
    - end_frame: Last frame to include (default: all)
    - team_id: Perspective (home/away)
    """
    from src.infrastructure.storage.phase_repository import phase_repository
    
    # Check if classification exists
    if not phase_repository.has_classification(match_id, team_id):
        return {
            "match_id": match_id,
            "team_id": team_id,
            "status": "not_classified",
            "message": "Phase data not yet available. Run classify-phases first.",
            "phases": [],
            "statistics": {
                "transition_count": 0,
                "phase_percentages": {}
            }
        }
    
    # Get statistics (fast, uses precomputed values)
    stats = phase_repository.get_statistics(match_id, team_id)
    
    # Get phases in range
    phases = phase_repository.get_phases_in_range(match_id, team_id, start_frame, end_frame)
    
    return {
        "match_id": match_id,
        "team_id": team_id,
        "status": "classified",
        "total_frames": stats.get("total_frames", 0),
        "phases": phases,
        "statistics": {
            "transition_count": stats.get("transition_count", 0),
            "phase_percentages": stats.get("phase_percentages", {}),
            "dominant_phase": stats.get("dominant_phase", "unknown")
        }
    }


@router.get("/matches/{match_id}/phases/transitions")
async def get_phase_transitions(match_id: str, team_id: str = "home"):
    """
    Get all phase transitions for a match.
    
    Returns list of transition events with frame numbers and timestamps.
    Useful for identifying key moments in the match.
    """
    from src.infrastructure.storage.phase_repository import phase_repository
    
    # Check if classification exists
    if not phase_repository.has_classification(match_id, team_id):
        return {
            "match_id": match_id,
            "team_id": team_id,
            "transitions": [],
            "message": "Run classify-phases first to generate transitions."
        }
    
    # Get transitions
    transitions = phase_repository.get_transitions(match_id, team_id)
    
    return {
        "match_id": match_id,
        "team_id": team_id,
        "transition_count": len(transitions),
        "transitions": [
            {
                "frame_id": t.frame_id,
                "timestamp": t.timestamp,
                "from_phase": t.from_phase.value,
                "to_phase": t.to_phase.value
            }
            for t in transitions
        ]
    }


@router.post("/classifiers/phase/train")
async def train_phase_classifier(request: TrainClassifierRequest):
    """
    Start training the phase classifier model.
    
    Requires labeled training data with features and phase labels.
    The trained model will be saved for future classification jobs.
    """
    task = celery_app.send_task(
        'train_phase_classifier',
        args=[request.training_data_path, f"/app/models/{request.model_name}.joblib"]
    )
    
    return {
        "job_id": task.id,
        "status": "PENDING",
        "message": f"Classifier training started from {request.training_data_path}",
    }
