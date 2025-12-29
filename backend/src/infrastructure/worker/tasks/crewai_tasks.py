"""
CrewAI Tasks - Infrastructure Layer

Celery tasks for running AI analysis using CrewAI.
"""
from celery import shared_task
import time

from src.infrastructure.adapters.crewai_adapter import CrewAIAdapter
from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
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
    
    Args:
        match_id: Match identifier
        
    Returns:
        Formatted string with match statistics
    """
    try:
        repo = PostgresMatchRepo()
        match = repo.get_match(match_id, source="statsbomb")
        
        if not match:
            return "Match not found in database."
        
        # Build context string
        context_lines = [
            f"Match: {match.home_team_id} vs {match.away_team_id}",
            f"Total Events: {len(match.events)}",
        ]
        
        # Count events by type
        from collections import Counter
        event_counts = Counter(event.event_type.value for event in match.events)
        
        context_lines.append("\nEvent Breakdown:")
        for event_type, count in event_counts.most_common():
            context_lines.append(f"  - {event_type}: {count}")
        
        # Get events by team (if available)
        team_events = {}
        for event in match.events:
            if event.team_id:
                if event.team_id not in team_events:
                    team_events[event.team_id] = []
                team_events[event.team_id].append(event)
        
        if team_events:
            context_lines.append("\nTeam Statistics:")
            for team_id, events in team_events.items():
                context_lines.append(f"  {team_id}: {len(events)} events")
        
        return "\n".join(context_lines)
        
    except Exception as e:
        return f"Error loading match context: {str(e)}"
