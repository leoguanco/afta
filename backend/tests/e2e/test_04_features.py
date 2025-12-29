
import pytest

API_URL = "http://localhost:8000/api/v1"
TEST_MATCH_ID = "3749133"

def test_pattern_detection(api_client):
    """Test pattern detection trigger."""
    payload = {"match_id": TEST_MATCH_ID}
    response = api_client.post(f"{API_URL}/patterns/detect", json=payload)
    
    assert response.status_code in [200, 202]
    data = response.json()
    assert "job_id" in data

def test_ai_analysis(api_client):
    """Test CrewAI analysis endpoint."""
    payload = {
        "match_id": TEST_MATCH_ID,
        "query": "Who was the key player in attack?"
    }
    response = api_client.post(f"{API_URL}/chat/analyze", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["match_id"] == TEST_MATCH_ID
