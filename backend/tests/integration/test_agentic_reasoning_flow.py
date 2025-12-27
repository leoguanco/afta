"""
Integration tests for Agentic Reasoning flow.

Tests the complete flow from API request to job completion.
"""
import pytest
from unittest.mock import Mock, patch
from src.application.use_cases.analyze_match import AnalyzeMatchUseCase
from src.domain.entities.analysis_job import AnalysisJob, JobStatus, AnalysisResult


class MockAnalysisPort:
    """Mock implementation of AnalysisPort for testing."""
    
    def __init__(self):
        self.dispatched_jobs = []
    
    def dispatch_analysis(self, match_id: str, query: str) -> str:
        """Mock dispatch that returns a predictable job_id."""
        job_id = f"job-{len(self.dispatched_jobs) + 1}"
        self.dispatched_jobs.append({
            'job_id': job_id,
            'match_id': match_id,
            'query': query
        })
        return job_id


def test_analyze_match_use_case():
    """Test the complete use case flow."""
    # Arrange
    mock_port = MockAnalysisPort()
    use_case = AnalyzeMatchUseCase(mock_port)
    
    # Act
    result = use_case.execute(
        match_id="match-123",
        query="What is the team's defensive strategy?"
    )
    
    # Assert
    assert result.job_id == "job-1"
    assert result.match_id == "match-123"
    assert result.status == "PENDING"
    assert len(mock_port.dispatched_jobs) == 1


def test_analysis_job_lifecycle():
    """Test complete job lifecycle from pending to completed."""
    # Create job
    job = AnalysisJob(
        job_id="job-test",
        match_id="match-123",
        query="Analyze pressing"
    )
    
    assert job.status == JobStatus.PENDING
    assert not job.is_terminal()
    
    # Start processing
    job.start_processing()
    assert job.status == JobStatus.RUNNING
    assert not job.is_terminal()
    
    # Complete
    result = AnalysisResult(
        content="The team uses a high pressing system.",
        tokens_used=200,
        duration_seconds=3.2
    )
    job.complete(result)
    
    assert job.status == JobStatus.COMPLETED
    assert job.is_terminal()
    assert job.result == result
    assert job.completed_at is not None


def test_analysis_job_failure_lifecycle():
    """Test job lifecycle when it fails."""
    job = AnalysisJob("job-fail", "match-123", "query")
    
    job.start_processing()
    job.fail("API timeout")
    
    assert job.status == JobStatus.FAILED
    assert job.is_terminal()
    assert job.error == "API timeout"
    assert job.completed_at is not None


@patch('src.infrastructure.worker.tasks.crewai_tasks.run_crewai_analysis_task')
def test_crewai_adapter_dispatch(mock_task):
    """Test that CrewAIAdapter correctly dispatches tasks."""
    from src.infrastructure.adapters.crewai_adapter import CrewAIAdapter
    
    # Mock the Celery task
    mock_task.delay.return_value.id = "celery-task-123"
    
    adapter = CrewAIAdapter()
    job_id = adapter.dispatch_analysis("match-456", "Analyze tactics")
    
    assert job_id == "celery-task-123"
    mock_task.delay.assert_called_once_with("match-456", "Analyze tactics")
