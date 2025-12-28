"""
IngestionPort - Domain Layer
"""
from abc import ABC, abstractmethod

class IngestionPort(ABC):
    @abstractmethod
    def start_ingestion(self, match_id: str, source: str) -> str:
        """Dispatch ingestion job. Returns job ID."""
        ...

"""
CalibrationPort - Domain Layer
"""
# Note: Splitting into separate files in real implementation
