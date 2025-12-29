"""
Test PhaseClassifier Use Case.
"""
import pytest
from unittest.mock import Mock, MagicMock
import pandas as pd

from src.application.use_cases.phase_classifier import PhaseClassifier
from src.domain.ports.phase_classifier_port import PhaseClassifierPort
from src.domain.ports.phase_repository import PhaseRepository
from src.domain.ports.object_storage_port import ObjectStoragePort
from src.domain.entities.phase_sequence import PhaseSequence
from src.domain.value_objects.game_phase import GamePhase

@pytest.fixture
def mock_ml_engine():
    engine = Mock(spec=PhaseClassifierPort)
    engine.is_trained.return_value = True
    return engine

@pytest.fixture
def mock_repo():
    return Mock(spec=PhaseRepository)

@pytest.fixture
def mock_storage():
    storage = Mock(spec=ObjectStoragePort)
    # Mock tracking data
    storage.get_parquet.return_value = pd.DataFrame({
        'frame_id': [1, 2],
        'team': ['home', 'home'],
        'player_id': ['p1', 'p1'],
        'x': [50.0, 51.0],
        'y': [30.0, 31.0],
        'ball_x': [60.0, 60.5],
        'ball_y': [35.0, 35.5]
    })
    return storage

def test_execute_success(mock_ml_engine, mock_repo, mock_storage):
    """Test successful execution of phase classification."""
    # Setup
    use_case = PhaseClassifier(mock_ml_engine, mock_repo, mock_storage)
    
    # Mock classification result (1 batch of 1 frame needs to return list of labels)
    # We have 2 frames in mock df.
    mock_ml_engine.classify_batch.return_value = [GamePhase.ORGANIZED_ATTACK, GamePhase.ORGANIZED_ATTACK]
    mock_ml_engine.classify_with_confidence.return_value = (GamePhase.ORGANIZED_ATTACK, 0.9)
    
    # Execute
    result = use_case.execute("match_123", "home")
    
    # Verify
    assert isinstance(result, PhaseSequence)
    assert result.match_id == "match_123"
    assert len(result) == 2
    
    # Verify interactions
    mock_storage.get_parquet.assert_called_once_with("tracking/match_123.parquet")
    mock_ml_engine.classify_batch.assert_called()
    mock_repo.save_phase_sequence.assert_called_once()

def test_execute_not_trained(mock_ml_engine, mock_repo, mock_storage):
    """Test execution fails if model not trained."""
    mock_ml_engine.is_trained.return_value = False
    
    use_case = PhaseClassifier(mock_ml_engine, mock_repo, mock_storage)
    
    with pytest.raises(ValueError, match="not trained"):
        use_case.execute("match_123")

def test_execute_missing_tracking(mock_ml_engine, mock_repo, mock_storage):
    """Test execution fails if tracking data missing."""
    mock_storage.get_parquet.side_effect = Exception("Not found")
    
    use_case = PhaseClassifier(mock_ml_engine, mock_repo, mock_storage)
    
    with pytest.raises(ValueError, match="Tracking data not found"):
        use_case.execute("match_123")
