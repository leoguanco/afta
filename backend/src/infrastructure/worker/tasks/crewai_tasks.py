"""
CrewAI Tasks - Infrastructure Layer

Celery tasks for running AI analysis using CrewAI.
"""
from collections import Counter
import time

from celery import shared_task
from prometheus_client import Histogram, Counter as PromCounter

from src.infrastructure.adapters.crewai_adapter import CrewAIAdapter
from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
from src.infrastructure.db.repositories.postgres_metrics_repo import PostgresMetricsRepository

# Metrics
llm_request_duration = Histogram(
    'llm_request_duration_seconds',
    'Duration of LLM requests',
    ['status']
)

llm_tokens_total = PromCounter(
    'llm_tokens_total',
    'Total tokens used by LLM',
    ['model']
)


@shared_task(name="run_crewai_analysis", queue="default")
def run_crewai_analysis_task(match_id: str, query: str) -> dict:
    """
    Run AI analysis using CrewAI.
    
    This task runs on the 'general' queue (CPU-bound).
    
    Args:
        match_id: Match identifier
        query: User's analysis query
        
    Returns:
        Dictionary with analysis result
    """
    start_time = time.time()
    
    try:
        # Build match context from database
        match_context = _build_match_context(match_id)
        
        # Initialize CrewAI and run analysis with context
        adapter = CrewAIAdapter()
        result_text = adapter.run_analysis(match_id, query, match_context)
        
        duration = time.time() - start_time
        
        # Record metrics
        llm_request_duration.labels(status='success').observe(duration)
        # Note: Token counting would require parsing LLM response metadata
        llm_tokens_total.labels(model='gpt-4o-mini').inc(100)  # Approximation
        
        return {
            'status': 'COMPLETED',
            'result': {
                'content': result_text,
                'model': 'gpt-4o-mini'
            },
            'duration': duration
        }
        
    except Exception as e:
        duration = time.time() - start_time
        llm_request_duration.labels(status='error').observe(duration)
        
        return {
            'status': 'FAILED',
            'error': str(e),
            'duration': duration
        }


def _build_match_context(match_id: str) -> str:
    """
    Build match context string from database.
    
    Delegates to shared MatchContextService.
    
    Args:
        match_id: Match identifier
        
    Returns:
        Formatted string with match statistics
    """
    from src.application.services.match_context_service import MatchContextService
    
    # Instantiate concrete logic here (Infrastructure Layer)
    repo = PostgresMatchRepo()
    metrics_repo = PostgresMetricsRepository()
    
    service = MatchContextService(repo, metrics_repo)
    return service.build_context(match_id)
