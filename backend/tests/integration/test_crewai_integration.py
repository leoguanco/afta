"""
Integration tests for CrewAI implementation.

Uses VCR to record/replay LLM API calls to avoid costs during testing.
"""

import pytest
from unittest.mock import patch, Mock

from src.infrastructure.adapters.crewai_adapter import CrewAIAdapter


class TestCrewAIIntegration:
    """Integration tests for CrewAI analysis."""

    @patch('src.infrastructure.adapters.crewai_adapter.ChatOpenAI')
    @patch('src.infrastructure.adapters.crewai_adapter.Crew')
    def test_analysis_flow_with_mock_llm(self, mock_crew_class, mock_llm_class):
        """
        Test full CrewAI analysis flow with mocked LLM.
        
        This avoids actual API calls while testing the orchestration logic.
        """
        # Arrange
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        mock_crew = Mock()
        mock_crew.kickoff.return_value = "Analysis complete: Strong defensive organization observed."
        mock_crew_class.return_value = mock_crew
        
        adapter = CrewAIAdapter()
        
        # Act
        result = adapter.run_analysis("match_123", "Analyze defensive tactics")
        
        # Assert
        assert "defensive organization" in result.lower()
        mock_crew.kickoff.assert_called_once()

    @patch('src.infrastructure.adapters.crewai_adapter.ChatOpenAI')
    def test_agent_creation(self, mock_llm_class):
        """Test that agents are created with correct configuration."""
        # Arrange
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        adapter = CrewAIAdapter()
        
        # Act
        agents = adapter.create_agents()
        
        # Assert
        assert "analyst" in agents
        assert "writer" in agents
        assert agents["analyst"].role == "Football Tactical Analyst"
        assert agents["writer"].role == "Sports Report Writer"

    @patch('src.infrastructure.adapters.crewai_adapter.ChatOpenAI')
    def test_task_creation(self, mock_llm_class):
        """Test that tasks are created with proper descriptions."""
        # Arrange
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        
        adapter = CrewAIAdapter()
        agents = adapter.create_agents()
        
        # Act
        tasks = adapter.create_tasks(agents, "match_456", "Analyze pressing intensity")
        
        # Assert
        assert len(tasks) == 2
        assert "pressing intensity" in tasks[0].description.lower()
        assert "report" in tasks[1].description.lower()


@pytest.mark.skipif(
    not pytest.config.getoption("--run-llm-tests", default=False),
    reason="Requires --run-llm-tests flag and valid OPENAI_API_KEY"
)
class TestCrewAIRealLLM:
    """
    Real LLM integration tests (only run with explicit flag).
    
    Run with: pytest --run-llm-tests
    """

    def test_real_analysis(self):
        """
        Test with actual LLM API call.
        
        WARNING: This will consume API credits.
        """
        import os
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")
        
        adapter = CrewAIAdapter()
        result = adapter.run_analysis("test_match", "What were the key tactical patterns?")
        
        assert len(result) > 100  # Should be a substantial response
        assert "tactical" in result.lower() or "pattern" in result.lower()
