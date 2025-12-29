
import pytest
import requests
import os
import time

# Use localhost:8000 for E2E tests running from host against Docker
API_URL = os.getenv("E2E_API_URL", "http://localhost:8000")

def wait_for_api(timeout=60):
    """Wait for API to be responsive."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{API_URL}/health")
            if r.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    return False

@pytest.fixture(scope="session")
def api_client():
    """Returns a configured requests session."""
    if not wait_for_api():
        pytest.fail(f"API at {API_URL} did not start in time")
    
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session
