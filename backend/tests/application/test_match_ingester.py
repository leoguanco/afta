"""
Test MatchIngester Use Case.
"""
import pytest
from unittest.mock import Mock

from src.application.use_cases.match_ingester import MatchIngester
from src.domain.ports.ingestion_port import IngestionPort

def test_execute():
    # Setup
    mock_dispatcher = Mock(spec=IngestionPort)
    mock_dispatcher.start_ingestion.return_value = "job_ingest_1"
    
    use_case = MatchIngester(mock_dispatcher)
    
    # Execute
    result = use_case.execute("match_123", "statsbomb")
    
    # Verify
    assert result.job_id == "job_ingest_1"
    assert result.status == "PENDING"
    mock_dispatcher.start_ingestion.assert_called_with("match_123", "statsbomb")
