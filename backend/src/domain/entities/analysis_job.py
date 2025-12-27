"""
AnalysisJob Entity - Domain Layer

Rich entity representing an AI analysis job with state management.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime


class JobStatus(Enum):
    """Analysis job status states."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class AnalysisResult:
    """Value object for analysis result."""
    content: str
    tokens_used: int = 0
    duration_seconds: float = 0.0


class AnalysisJob:
    """
    Rich domain entity representing an AI analysis job.
    
    Encapsulates job state and enforces valid state transitions.
    """
    
    def __init__(
        self,
        job_id: str,
        match_id: str,
        query: str,
        status: JobStatus = JobStatus.PENDING
    ):
        """
        Initialize analysis job.
        
        Args:
            job_id: Unique job identifier
            match_id: Match being analyzed
            query: User's analysis query
            status: Initial status
        """
        self.job_id = job_id
        self.match_id = match_id
        self.query = query
        self.status = status
        self.result: Optional[AnalysisResult] = None
        self.error: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
    
    def start_processing(self) -> None:
        """
        Transition job to RUNNING state.
        
        Raises:
            ValueError: If job is not in PENDING state
        """
        if self.status != JobStatus.PENDING:
            raise ValueError(
                f"Cannot start job in {self.status.value} state"
            )
        self.status = JobStatus.RUNNING
    
    def complete(self, result: AnalysisResult) -> None:
        """
        Mark job as completed with result.
        
        Args:
            result: Analysis result
            
        Raises:
            ValueError: If job is not in RUNNING state
        """
        if self.status != JobStatus.RUNNING:
            raise ValueError(
                f"Cannot complete job in {self.status.value} state"
            )
        self.status = JobStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.utcnow()
    
    def fail(self, error: str) -> None:
        """
        Mark job as failed with error.
        
        Args:
            error: Error message
            
        Raises:
            ValueError: If job is already completed
        """
        if self.status == JobStatus.COMPLETED:
            raise ValueError("Cannot fail a completed job")
        
        self.status = JobStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()
    
    def is_terminal(self) -> bool:
        """Check if job is in a terminal state."""
        return self.status in (JobStatus.COMPLETED, JobStatus.FAILED)
    
    def __repr__(self) -> str:
        return f"AnalysisJob(job_id={self.job_id}, status={self.status.value})"
