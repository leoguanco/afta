"""
JSONExporter - Infrastructure Layer

Exports TacticalReport to structured JSON format.
"""
import json
from typing import Dict, Any
from datetime import datetime

from src.domain.entities.tactical_report import TacticalReport
from src.domain.value_objects.report_section import ContentType


class JSONExporter:
    """
    Exports tactical reports to JSON format.
    
    Follows a versioned schema for compatibility.
    """
    
    SCHEMA_VERSION = "1.0"
    
    def export(self, report: TacticalReport) -> str:
        """
        Export report to JSON string.
        
        Args:
            report: TacticalReport entity
            
        Returns:
            Formatted JSON string
        """
        data = self._build_export_data(report)
        return json.dumps(data, indent=2, default=self._json_serializer)
    
    def export_to_dict(self, report: TacticalReport) -> Dict[str, Any]:
        """
        Export report to dictionary.
        
        Args:
            report: TacticalReport entity
            
        Returns:
            Dictionary representation
        """
        return self._build_export_data(report)
    
    def _build_export_data(self, report: TacticalReport) -> Dict[str, Any]:
        """Build the export data structure."""
        return {
            "schema_version": self.SCHEMA_VERSION,
            "export_timestamp": datetime.utcnow().isoformat(),
            "report": {
                "id": report.report_id,
                "match_id": report.match_id,
                "team_id": report.team_id,
                "title": report.title,
                "created_at": report.created_at.isoformat(),
                "metadata": report.metadata,
            },
            "sections": [
                self._serialize_section(s) for s in report.sections
            ],
            "summary": {
                "total_sections": report.section_count(),
                "section_types": self._count_section_types(report)
            }
        }
    
    def _serialize_section(self, section) -> Dict[str, Any]:
        """Serialize a single section."""
        content = section.content
        
        # Handle binary content (charts)
        if section.content_type == ContentType.CHART:
            content = "[BINARY_CHART_DATA]"
        
        return {
            "title": section.title,
            "type": section.content_type.value,
            "order": section.order,
            "description": section.description,
            "content": content
        }
    
    def _count_section_types(self, report: TacticalReport) -> Dict[str, int]:
        """Count sections by type."""
        counts = {}
        for section in report.sections:
            type_name = section.content_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    @staticmethod
    def _json_serializer(obj):
        """Custom JSON serializer for non-standard types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return "[BINARY_DATA]"
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
