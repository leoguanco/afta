
import pytest
import requests
import os

API_URL = os.getenv("E2E_API_URL", "http://localhost:8000")

def test_health_check(api_client):
    """Verify system health endpoint returns 200 and healthy components."""
    response = api_client.get(f"{API_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["redis"] == "connected"

def test_metrics_endpoint(api_client):
    """Verify Prometheus metrics are exposed."""
    response = api_client.get(f"{API_URL}/metrics")
    assert response.status_code == 200
    assert "process_cpu_seconds_total" in response.text
