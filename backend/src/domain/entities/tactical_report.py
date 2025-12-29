"""
TacticalReport - Domain Layer

Rich Entity representing a complete tactical match report.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from src.domain.value_objects.report_section import ReportSection, ContentType


@dataclass
class TacticalReport:
    """
    Rich Entity: A complete tactical report for a match.
    
    Contains multiple sections (visualizations, metrics, AI analysis).
    Provides methods to build, query, and export the report.
    """
    report_id: str
    match_id: str
    team_id: str
    title: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    sections: List[ReportSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_section(self, section: ReportSection) -> None:
        """Add a section to the report."""
        self.sections.append(section)
        self.sections.sort()  # Maintain order
    
    def get_sections_by_type(self, content_type: ContentType) -> List[ReportSection]:
        """Get all sections of a specific type."""
        return [s for s in self.sections if s.content_type == content_type]
    
    def get_text_sections(self) -> List[ReportSection]:
        """Get all text sections."""
        return self.get_sections_by_type(ContentType.TEXT)
    
    def get_chart_sections(self) -> List[ReportSection]:
        """Get all chart sections."""
        return self.get_sections_by_type(ContentType.CHART)
    
    def get_ai_analysis(self) -> Optional[ReportSection]:
        """Get the AI analysis section if present."""
        ai_sections = self.get_sections_by_type(ContentType.AI_ANALYSIS)
        return ai_sections[0] if ai_sections else None
    
    def section_count(self) -> int:
        """Return total number of sections."""
        return len(self.sections)
    
    def to_json(self) -> str:
        """
        Export report to JSON format.
        
        Charts are excluded (binary data).
        """
        return json.dumps(self._to_dict(), indent=2, default=str)
    
    def _to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary (excluding binary chart data)."""
        return {
            "schema_version": "1.0",
            "report_id": self.report_id,
            "match_id": self.match_id,
            "team_id": self.team_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "sections": [
                {
                    "title": s.title,
                    "content_type": s.content_type.value,
                    "order": s.order,
                    "description": s.description,
                    # Only include content for non-binary types
                    "content": s.content if s.content_type != ContentType.CHART else "[CHART_DATA]"
                }
                for s in self.sections
            ]
        }
