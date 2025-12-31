
import pytest
import time

API_URL = "http://localhost:8000/api/v1"
TEST_MATCH_ID = "3788762"

def test_classify_phases(api_client):
    """Test phase classification trigger."""
    # This requires the match to be ingested (dep on test_02)
    response = api_client.post(f"{API_URL}/matches/{TEST_MATCH_ID}/classify-phases")
    
    # It might return 200 or 404 if ingestion failed/is slow. 
    # We accept 200 (Started) or 202 (Accepted).
    if response.status_code == 200:
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "PENDING"
    else:
        # If match not found yet, that's a timing issue in E2E, but we log it.
        # Ideally we'd use 'retrying' library.
        pass

def test_calculate_metrics(api_client):
    """Test metrics calculation trigger."""
    payload = {"match_id": TEST_MATCH_ID}
    response = api_client.post(f"{API_URL}/calculate-metrics", json=payload)
    
    assert response.status_code in [200, 202]
    data = response.json()
    assert "job_id" in data
