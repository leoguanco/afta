"""
ReportSection - Domain Layer

Value Object representing a section of a tactical report.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any


class ContentType(str, Enum):
    """Types of content that can appear in a report section."""
    TEXT = "text"
    CHART = "chart"
    TABLE = "table"
    METRICS = "metrics"
    AI_ANALYSIS = "ai_analysis"


@dataclass(frozen=True)
class ReportSection:
    """
    Value Object: A single section in a tactical report.
    
    Immutable. Contains title, content, and ordering information.
    """
    title: str
    content_type: ContentType
    content: Any  # Text, chart bytes, table data, etc.
    order: int = 0
    description: Optional[str] = None
    
    def __lt__(self, other: "ReportSection") -> bool:
        """Enable sorting by order."""
        return self.order < other.order
