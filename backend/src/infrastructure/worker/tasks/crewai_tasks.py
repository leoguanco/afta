"""
CrewAI Tasks - Infrastructure Layer

Celery tasks for running AI analysis using CrewAI.
"""
from celery import shared_task
import time

from src.infrastructure.adapters.crewai_adapter import CrewAIAdapter
from prometheus_client import Histogram, Counter

# Metrics
llm_request_duration = Histogram(
    'llm_request_duration_seconds',
    'Duration of LLM requests',
    ['status']
)

llm_tokens_total = Counter(
    'llm_tokens_total',
    'Total tokens used by LLM',
    ['model']
)


@shared_task(name="run_crewai_analysis", queue="general")
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
        # Initialize CrewAI and run analysis
        adapter = CrewAIAdapter()
        result_text = adapter.run_analysis(match_id, query)
        
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
