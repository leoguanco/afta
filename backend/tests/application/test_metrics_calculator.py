"""
Test MetricsCalculator Use Case.
"""
import pytest
from unittest.mock import Mock

from src.application.use_cases.metrics_calculator import MetricsCalculator
from src.domain.ports.metrics_repository import MetricsRepository

@pytest.fixture
def mock_repo():
    return Mock(spec=MetricsRepository)

def test_execute(mock_repo):
    """Test successful metrics calculation."""
    use_case = MetricsCalculator(mock_repo)
    
    # Dummy data
    tracking_data = [
        {"frame_id": 1, "player_id": "p1", "x": 10, "y": 10, "timestamp": 0.0},
        {"frame_id": 2, "player_id": "p1", "x": 11, "y": 11, "timestamp": 0.04},
        {"frame_id": 1, "player_id": "p2", "x": 20, "y": 20, "timestamp": 0.0}, # Team 2
    ]
    # Need team_id inside tracking data for match frames
    tracking_data[0]["team_id"] = "home"
    tracking_data[1]["team_id"] = "home"
    tracking_data[2]["team_id"] = "away"
    
    event_data = [
        {"event_id": "e1", "event_type": "PASS", "team_id": "home", "player_id": "p1", "timestamp": 0.1, "x": 10, "y": 10}
    ]
    
    result = use_case.execute("match_123", tracking_data, event_data)
    
    # Verify result object
    assert result.match_id == "match_123"
    assert result.players_processed == 2
    
    # Verify repository calls
    mock_repo.save_physical_stats.assert_called()
    mock_repo.save_pitch_control_frame.assert_called() # Should be called for frame 1? (Sample rate check)
    mock_repo.save_ppda.assert_called()
