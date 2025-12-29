
import pytest
import time

API_URL = "http://localhost:8000/api/v1"
TEST_MATCH_ID = "3749133"

def test_generate_report(api_client):
    """Test PDF report generation."""
    payload = {"match_id": TEST_MATCH_ID, "include_ai_analysis": True}
    response = api_client.post(f"{API_URL}/reports/generate", json=payload)
    
    assert response.status_code in [200, 202]
    data = response.json()
    job_id = data["job_id"]
    
    # Poll for completion (Max 120s)
    max_retries = 1500
    for _ in range(max_retries):
        r = api_client.get(f"{API_URL}/reports/jobs/{job_id}")
        assert r.status_code == 200
        status = r.json()["status"]
        
        if status == "COMPLETED":
            # Verify download URL
            assert "download_url" in r.json()
            return
        elif status == "FAILED":
            pytest.fail(f"Report generation failed: {r.json().get('error')}")
            
        time.sleep(2)
        
    pytest.fail("Report generation timed out")
