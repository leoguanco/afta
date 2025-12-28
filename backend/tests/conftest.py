"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# --- MOCKS FOR MISSING DEPENDENCIES ---
from unittest.mock import MagicMock

# --- MOCKS FOR MISSING DEPENDENCIES ---
from unittest.mock import MagicMock

# Force Mock CrewAI
print("Forcing mock for crewai...")
class FakeAgent:
    def __init__(self, role=None, goal=None, backstory=None, **kwargs):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        
class FakeTask:
    def __init__(self, description=None, expected_output=None, agent=None, **kwargs):
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
        
class FakeCrew:
    def __init__(self, agents=None, tasks=None, **kwargs):
        pass
    def kickoff(self):
        return "Mock Result"

mock_crewai = MagicMock()
mock_crewai.Agent = FakeAgent
mock_crewai.Task = FakeTask
mock_crewai.Crew = FakeCrew
sys.modules["crewai"] = mock_crewai

# Force Mock LangChain
print("Forcing mock for langchain_openai...")
mock_lc = MagicMock()
sys.modules["langchain_openai"] = mock_lc

# Force Mock MinIO
print("Forcing mock for minio...")
class FakeS3Error(Exception):
    def __init__(self, code=None, message=None, **kwargs):
        self.code = code
        self.message = message
        
mock_minio_pkg = MagicMock()
mock_minio_error = MagicMock()
mock_minio_error.S3Error = FakeS3Error
mock_minio_pkg.error = mock_minio_error
sys.modules["minio"] = mock_minio_pkg
sys.modules["minio.error"] = mock_minio_error

# Force Mock StatsBomb
print("Forcing mock for statsbombpy...")
sys.modules["statsbombpy"] = MagicMock()

# Force Mock CV2
print("Forcing mock for cv2...")
sys.modules["cv2"] = MagicMock()

# Force Mock Ultralytics
print("Forcing mock for ultralytics...")
sys.modules["ultralytics"] = MagicMock()





