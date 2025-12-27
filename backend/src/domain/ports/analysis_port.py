"""
AnalysisPort - Domain Layer

Port for dispatching AI analysis jobs to background workers.
"""
from abc import ABC, abstractmethod


class AnalysisPort(ABC):
    """
    Port for dispatching analysis jobs to AI workers.
    """
    
    @abstractmethod
    def dispatch_analysis(self, match_id: str, query: str) -> str:
        """
        Dispatch an analysis job.
        
        Args:
            match_id: Match identifier to analyze
            query: User's analysis query
            
        Returns:
            Job ID (task ID)
        """
        pass
