"""
Fake implementations for testing (Test Doubles).

These are in-memory implementations of Domain Ports that don't require
external dependencies. Following Hexagonal Architecture, tests inject these
instead of using mock.patch.
"""
from typing import Optional, Dict, List
from src.domain.entities.match import Match
from src.domain.ports.match_repository import MatchRepository
from src.domain.ports.storage_port import StoragePort
from src.domain.ports.analysis_port import AnalysisPort
import pandas as pd
import io


class FakeMatchRepository(MatchRepository):
    """In-memory Match Repository for testing."""
    
    def __init__(self):
        self.matches: Dict[str, Match] = {}
    
    def get_match(self, match_id: str, source: str) -> Optional[Match]:
        """Retrieve match from in-memory store."""
        return self.matches.get(match_id)
    
    def save(self, match: Match) -> None:
        """Save match to in-memory store."""
        self.matches[match.match_id] = match


class FakeStorageAdapter(StoragePort):
    """In-memory Storage Adapter for testing."""
    
    def __init__(self):
        self.storage: Dict[str, bytes] = {}
    
    def save_parquet(self, object_name: str, data: pd.DataFrame) -> None:
        """Save DataFrame as parquet bytes in memory."""
        buffer = io.BytesIO()
        data.to_parquet(buffer, engine='pyarrow', index=False)
        self.storage[object_name] = buffer.getvalue()
    
    def get_parquet(self, object_name: str) -> pd.DataFrame:
        """Retrieve DataFrame from memory."""
        if object_name not in self.storage:
            raise FileNotFoundError(f"Object {object_name} not found")
        buffer = io.BytesIO(self.storage[object_name])
        return pd.read_parquet(buffer, engine='pyarrow')


class FakeAnalysisAdapter(AnalysisPort):
    """Deterministic Analysis Adapter for testing."""
    
    def __init__(self, canned_response: str = "Fake analysis result"):
        self.canned_response = canned_response
        self.calls: List[Dict[str, str]] = []
    
    def run_analysis(self, match_id: str, query: str, match_context: str = "") -> str:
        """Return canned response and record the call."""
        self.calls.append({
            'match_id': match_id,
            'query': query,
            'match_context': match_context
        })
        return self.canned_response
