"""
Unit tests for AnalysisJob entity.

Following TDD principles to verify state transition logic.
"""
import pytest
from datetime import datetime
from src.domain.entities.analysis_job import (
    AnalysisJob,
    JobStatus,
    AnalysisResult
)


def test_analysis_job_creation():
    """Test that a new job is created in PENDING state."""
    job = AnalysisJob(
        job_id="job-123",
        match_id="match-456",
        query="What is the team's pressing intensity?"
    )
    
    assert job.job_id == "job-123"
    assert job.match_id == "match-456"
    assert job.status == JobStatus.PENDING
    assert job.result is None
    assert job.error is None
    assert job.completed_at is None


def test_start_processing_from_pending():
    """Test successful transition from PENDING to RUNNING."""
    job = AnalysisJob("job-1", "match-1", "query")
    
    job.start_processing()
    
    assert job.status == JobStatus.RUNNING


def test_start_processing_from_running_fails():
    """Test that starting an already running job raises error."""
    job = AnalysisJob("job-1", "match-1", "query")
    job.start_processing()
    
    with pytest.raises(ValueError, match="Cannot start job in RUNNING state"):
        job.start_processing()


def test_start_processing_from_completed_fails():
    """Test that starting a completed job raises error."""
    job = AnalysisJob("job-1", "match-1", "query")
    job.start_processing()
    result = AnalysisResult(content="Analysis result", tokens_used=100)
    job.complete(result)
    
    with pytest.raises(ValueError, match="Cannot start job in COMPLETED state"):
        job.start_processing()


def test_complete_job_from_running():
    """Test successful completion of a running job."""
    job = AnalysisJob("job-1", "match-1", "query")
    job.start_processing()
    
    result = AnalysisResult(
        content="The team shows high pressing intensity.",
        tokens_used=150,
        duration_seconds=2.5
    )
    job.complete(result)
    
    assert job.status == JobStatus.COMPLETED
    assert job.result == result
    assert job.error is None
    assert job.completed_at is not None


def test_complete_job_from_pending_fails():
    """Test that completing a pending job raises error."""
    job = AnalysisJob("job-1", "match-1", "query")
    result = AnalysisResult(content="Result")
    
    with pytest.raises(ValueError, match="Cannot complete job in PENDING state"):
        job.complete(result)


def test_fail_job_from_running():
    """Test failing a running job."""
    job = AnalysisJob("job-1", "match-1", "query")
    job.start_processing()
    
    job.fail("LLM API timeout")
    
    assert job.status == JobStatus.FAILED
    assert job.error == "LLM API timeout"
    assert job.result is None
    assert job.completed_at is not None


def test_fail_job_from_pending():
    """Test failing a pending job."""
    job = AnalysisJob("job-1", "match-1", "query")
    
    job.fail("Invalid match_id")
    
    assert job.status == JobStatus.FAILED
    assert job.error == "Invalid match_id"


def test_fail_completed_job_raises_error():
    """Test that failing a completed job raises error."""
    job = AnalysisJob("job-1", "match-1", "query")
    job.start_processing()
    result = AnalysisResult(content="Result")
    job.complete(result)
    
    with pytest.raises(ValueError, match="Cannot fail a completed job"):
        job.fail("Error")


def test_is_terminal():
    """Test terminal state detection."""
    job = AnalysisJob("job-1", "match-1", "query")
    
    assert not job.is_terminal()
    
    job.start_processing()
    assert not job.is_terminal()
    
    result = AnalysisResult(content="Result")
    job.complete(result)
    assert job.is_terminal()


def test_is_terminal_failed():
    """Test terminal state for failed jobs."""
    job = AnalysisJob("job-1", "match-1", "query")
    job.fail("Error")
    
    assert job.is_terminal()
