"""
Metrics Tasks - Infrastructure Layer

Celery tasks for calculating tactical metrics in the background.
"""
from typing import List, Dict, Any
from celery import shared_task

# Application use case
from src.application.use_cases.metrics_calculator import MetricsCalculator

# Infrastructure
from src.infrastructure.storage.metrics_repo import MetricsRepository


@shared_task(name="calculate_match_metrics")
def calculate_match_metrics_task(
    match_id: str,
    tracking_data: List[Dict[str, Any]],
    event_data: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Calculate all tactical metrics for a match.
    
    Delegates to application use case for orchestration.
    
    Args:
        match_id: Match identifier
        tracking_data: List of tracking frames with player positions
        event_data: List of match events
        
    Returns:
        Status dictionary with calculation results
    """
    # Initialize infrastructure dependencies
    repository = MetricsRepository()
    
    # Execute use case
    use_case = MetricsCalculator(repository)
    result = use_case.execute(match_id, tracking_data, event_data)
    
    # Persist results
    repository.flush(match_id)
    
    return {
        "status": result.status,
        "match_id": result.match_id,
        "players_processed": result.players_processed,
        "frames_processed": result.frames_processed,
        "events_processed": result.events_processed
    }

