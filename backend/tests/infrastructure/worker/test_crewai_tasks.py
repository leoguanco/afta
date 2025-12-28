"""
Unit tests for CrewAI Tasks.
"""

import pytest
from unittest.mock import Mock, patch
from src.infrastructure.worker.tasks.crewai_tasks import run_crewai_analysis_task

class TestCrewAITasks:
    """Test suite for CrewAI Tasks."""

    @patch('src.infrastructure.worker.tasks.crewai_tasks.PostgresMatchRepo')
    @patch('src.infrastructure.worker.tasks.crewai_tasks.CrewAIAdapter')
    def test_task_injects_match_context(self, mock_adapter_cls, mock_repo_cls):
        """Test that the task builds context and passes it to the adapter."""
        # Arrange
        # Mock Repository
        mock_repo = Mock()
        mock_match = Mock()
        mock_match.home_team_id = "Team A"
        mock_match.away_team_id = "Team B"
        mock_match.events = [Mock(event_type=Mock(value="Pass")), Mock(event_type=Mock(value="Shot"))]
        mock_repo.get_match.return_value = mock_match
        mock_repo_cls.return_value = mock_repo
        
        # Mock Adapter
        mock_adapter = Mock()
        mock_adapter.run_analysis.return_value = "Report"
        mock_adapter_cls.return_value = mock_adapter

        # Act
        result = run_crewai_analysis_task("match_123", "analysis query")

        # Assert
        # 1. Verify Repo was queried
        mock_repo.get_match.assert_called_with("match_123", source="statsbomb")
        
        # 2. Verify Adapter was called with context
        mock_adapter.run_analysis.assert_called_once()
        call_args = mock_adapter.run_analysis.call_args
        
        # Check args: match_id, query, context
        assert call_args[0][0] == "match_123"
        assert call_args[0][1] == "analysis query"
        context_arg = call_args[0][2]
        
        # Verify context content
        assert "Team A vs Team B" in context_arg
        assert "Total Events: 2" in context_arg
        assert "Pass: 1" in context_arg
