"""
Metrics Tasks - Infrastructure Layer

Celery tasks for calculating tactical metrics in the background.
"""
import logging
from typing import List, Dict, Any
from celery import shared_task

# Application use case
from src.application.use_cases.metrics_calculator import MetricsCalculator

# Infrastructure
from src.infrastructure.db.repositories.postgres_metrics_repo import PostgresMetricsRepository
from src.infrastructure.di.container import Container

logger = logging.getLogger(__name__)


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
    repository = PostgresMetricsRepository()
    
    try:
        # Execute use case
        use_case = MetricsCalculator(repository)
        result = use_case.execute(match_id, tracking_data, event_data)
        
        # --- RAG Indexing ---
        try:
            indexer = Container.get_match_data_indexer()
            
            # Build metrics summary for indexing
            metrics_for_indexing = {
                "players_processed": result.players_processed,
                "frames_processed": result.frames_processed,
                "events_processed": result.events_processed,
            }
            
            # Add aggregate metrics if available
            if hasattr(result, 'aggregate_metrics') and result.aggregate_metrics:
                metrics_for_indexing.update(result.aggregate_metrics)
            
            index_result = indexer.execute(
                match_id=match_id,
                match_metrics=metrics_for_indexing
            )
            logger.info(f"RAG indexed {index_result.documents_indexed} metric documents")
        except Exception as index_err:
            # Don't fail metrics calculation if indexing fails
            logger.warning(f"RAG indexing failed (non-critical): {index_err}")
        
        return {
            "status": result.status,
            "match_id": result.match_id,
            "players_processed": result.players_processed,
            "frames_processed": result.frames_processed,
            "events_processed": result.events_processed
        }
    finally:
        repository.close()
