"""
Unit tests for Phase Classification Tasks.
"""
import pytest
from unittest.mock import Mock, patch

from src.infrastructure.worker.tasks.phase_classification_tasks import classify_match_phases_task

class TestPhaseClassificationTasks:
    """Test suite for phase classification celery tasks."""

    @patch('src.infrastructure.worker.tasks.phase_classification_tasks.PhaseClassifier')
    @patch('src.infrastructure.worker.tasks.phase_classification_tasks.SklearnPhaseClassifier')
    @patch('src.infrastructure.worker.tasks.phase_classification_tasks.MinIOAdapter')
    @patch('src.infrastructure.worker.tasks.phase_classification_tasks.phase_repository')
    def test_classify_match_phases_missing_tracking_data(
        self, 
        mock_repo, 
        mock_minio, 
        mock_sklearn, 
        mock_use_case_cls
    ):
        """Test that missing tracking data returns a skipped status, not error."""
        # Arrange
        mock_use_case = Mock()
        mock_use_case.execute.side_effect = ValueError("Tracking data not found for match 123")
        mock_use_case_cls.return_value = mock_use_case
        
        # Act
        result = classify_match_phases_task("match_123")
        
        # Assert
        assert result["status"] == "skipped"
        assert result["reason"] == "tracking_data_missing"
        assert "Tracking data not found" in result["message"]

    @patch('src.infrastructure.worker.tasks.phase_classification_tasks.PhaseClassifier')
    @patch('src.infrastructure.worker.tasks.phase_classification_tasks.SklearnPhaseClassifier')
    @patch('src.infrastructure.worker.tasks.phase_classification_tasks.MinIOAdapter')
    @patch('src.infrastructure.worker.tasks.phase_classification_tasks.phase_repository')
    def test_classify_match_phases_generic_error(
        self, 
        mock_repo, 
        mock_minio, 
        mock_sklearn, 
        mock_use_case_cls
    ):
        """Test that generic errors return error status."""
        # Arrange
        mock_use_case = Mock()
        mock_use_case.execute.side_effect = Exception("Unexpected failure")
        mock_use_case_cls.return_value = mock_use_case
        
        # Act
        result = classify_match_phases_task("match_123")
        
        # Assert
        assert result["status"] == "error"
        assert "Unexpected failure" in result["message"]
