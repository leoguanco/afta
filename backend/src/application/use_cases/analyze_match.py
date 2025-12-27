"""
AnalyzeMatch Use Case - Application Layer

Orchestrates AI analysis by dispatching jobs and managing state.
"""
from dataclasses import dataclass
from src.domain.ports.analysis_port import AnalysisPort


@dataclass
class AnalysisJobStarted:
    """Result of starting an analysis job."""
    job_id: str
    match_id: str
    status: str = "PENDING"


class AnalyzeMatchUseCase:
    """
    Application use case for analyzing matches with AI.
    
    Delegates to infrastructure via AnalysisPort.
    """
    
    def __init__(self, analysis_port: AnalysisPort):
        """
        Initialize use case.
        
        Args:
            analysis_port: Port for dispatching analysis jobs
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
