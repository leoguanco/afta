"""
Test MatchAnalyzer Use Case.
"""
import pytest
from unittest.mock import Mock

from src.application.use_cases.match_analyzer import MatchAnalyzer
from src.domain.ports.analysis_port import AnalysisPort

def test_execute():
    # Setup
    mock_dispatcher = Mock(spec=AnalysisPort)
    mock_dispatcher.dispatch_analysis.return_value = "job_analysis_1"
    
    use_case = MatchAnalyzer(mock_dispatcher)
    
    # Execute
    result = use_case.execute("match_123", "Who won?")
    
    # Verify
    assert result.job_id == "job_analysis_1"
    assert result.status == "PENDING"
    mock_dispatcher.dispatch_analysis.assert_called_with("match_123", "Who won?")
