"""
Test JSONExporter.
"""
import pytest
import json
from datetime import datetime

from src.infrastructure.reports.json_exporter import JSONExporter
from src.domain.entities.tactical_report import TacticalReport
from src.domain.value_objects.report_section import ReportSection, ContentType


@pytest.fixture
def sample_report():
    """Create a sample report for testing."""
    report = TacticalReport(
        report_id="test123",
        match_id="match456",
        team_id="home",
        title="Test Match Report"
    )
    
    report.add_section(ReportSection(
        title="Summary",
        content_type=ContentType.TEXT,
        content="This is a test summary",
        order=1
    ))
    
    report.add_section(ReportSection(
        title="Metrics",
        content_type=ContentType.METRICS,
        content={"possession": "60%", "shots": "12"},
        order=2
    ))
    
    return report


def test_export(sample_report):
    """Test JSON export."""
    exporter = JSONExporter()
    json_str = exporter.export(sample_report)
    
    # Should be valid JSON
    data = json.loads(json_str)
    
    assert data["schema_version"] == "1.0"
    assert data["report"]["id"] == "test123"
    assert data["report"]["match_id"] == "match456"
    assert len(data["sections"]) == 2


def test_export_to_dict(sample_report):
    """Test exporting to dictionary."""
    exporter = JSONExporter()
    data = exporter.export_to_dict(sample_report)
    
    assert isinstance(data, dict)
    assert "report" in data
    assert "sections" in data
    assert "summary" in data


def test_section_type_counts(sample_report):
    """Test section type counting."""
    exporter = JSONExporter()
    data = exporter.export_to_dict(sample_report)
    
    assert data["summary"]["total_sections"] == 2
    assert data["summary"]["section_types"]["text"] == 1
    assert data["summary"]["section_types"]["metrics"] == 1
