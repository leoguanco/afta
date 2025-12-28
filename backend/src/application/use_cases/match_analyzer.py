"""
MatchAnalyzer - Application Layer

Use Case for analyzing matches with AI (RAG/LLM).
"""
from dataclasses import dataclass
from src.domain.ports.analysis_port import AnalysisPort


@dataclass
class AnalysisJobStarted:
    """Result of starting an analysis job."""
    job_id: str
    match_id: str
    status: str = "PENDING"


class MatchAnalyzer:
    """
    Use Case: Analyze Match.
    
    Delegates to AnalysisPort for execution (sync or async).
    For API usage, typically dispatches an async job.
    """
    
    def __init__(self, analysis_port: AnalysisPort):
        """
        Initialize with analysis port.
        """
        self.analysis_port = analysis_port
    
    def execute(self, match_id: str, query: str) -> AnalysisJobStarted:
        """
        Start an analysis job.
        
        Args:
            match_id: Match to analyze
            query: User's analysis question
            
        Returns:
            AnalysisJobStarted with job_id
        """
        job_id = self.analysis_port.dispatch_analysis(match_id, query)
        
        return AnalysisJobStarted(
            job_id=job_id,
            match_id=match_id
        )
