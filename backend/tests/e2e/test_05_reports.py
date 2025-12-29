
import pytest

API_URL = "http://localhost:8000/api/v1"
TEST_MATCH_ID = "3749133"

def test_generate_report(api_client):
    """Test PDF report generation."""
    payload = {"match_id": TEST_MATCH_ID, "include_ai_analysis": True}
    response = api_client.post(f"{API_URL}/reports/generate", json=payload)
    
    assert response.status_code in [200, 202]
    data = response.json()
    assert "job_id" in data
