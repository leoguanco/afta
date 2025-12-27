"""
CrewAI Adapter - Infrastructure Layer

Implementation of AnalysisPort using Celery for async job dispatch.
"""
from typing import List, Dict, Any
from src.domain.ports.analysis_port import AnalysisPort
from src.infrastructure.worker.tasks.crewai_tasks import run_crewai_analysis_task


class CrewAIAdapter(AnalysisPort):
    """
    Celery-based implementation of the AnalysisPort.
    
    Dispatches analysis jobs to background workers.
    """
    
    def dispatch_analysis(self, match_id: str, query: str) -> str:
        """
        Dispatch analysis job to Celery worker.
        
        Args:
            match_id: Match identifier
            query: User's analysis query
            
        Returns:
            Job ID (Celery task ID)
        """
        task = run_crewai_analysis_task.delay(match_id, query)
        return task.id
