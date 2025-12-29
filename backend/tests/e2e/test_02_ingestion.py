
import pytest
import time

API_URL = "http://localhost:8000/api/v1"
TEST_MATCH_ID = "3749133"  # Common StatsBomb sample match

def test_ingest_match(api_client):
    """Test full ingestion workflow for a StatsBomb match."""
    # 1. Trigger Ingestion
    payload = {"match_id": TEST_MATCH_ID, "source": "statsbomb"}
    response = api_client.post(f"{API_URL}/ingest", json=payload)
    
    # Assert Accepted
    assert response.status_code in [200, 202]
    data = response.json()
    job_id = data["job_id"]
    assert job_id is not None

    # 2. Poll for Completion (Max 120s)
    max_retries = 1500
    for _ in range(max_retries):
        r = api_client.get(f"{API_URL}/matches/{TEST_MATCH_ID}")
        if r.status_code == 200:
            match_data = r.json()
            assert match_data["match_id"] == TEST_MATCH_ID
            assert match_data["event_count"] > 0
            return  # Success
        time.sleep(2)
        
    pytest.fail(f"Ingestion timed out for match {TEST_MATCH_ID}") 
