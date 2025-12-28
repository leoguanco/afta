"""
AnalysisPort - Domain Layer

Port for running AI analysis on match data.
"""
from abc import ABC, abstractmethod


class AnalysisPort(ABC):
    """
    Port for running AI analysis on match data.
    """
    
    @abstractmethod
    def run_analysis(self, match_id: str, query: str, match_context: str = "") -> str:
        """
        Run synchronous AI analysis.
        
        Args:
            match_id: Match identifier to analyze
            query: User's analysis query
            match_context: Additional match context/statistics
            
        Returns:
            Analysis result as string
        """
        pass

    @abstractmethod
    def dispatch_analysis(self, match_id: str, query: str) -> str:
        """
        Dispatch asynchronous AI analysis job.
        
        Args:
            match_id: Match identifier
            query: User's analysis query
            
        Returns:
            Job ID of the dispatched task
        """
        pass
