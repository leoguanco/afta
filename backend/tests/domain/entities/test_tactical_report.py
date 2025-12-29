"""
Test TacticalReport Entity.
"""
import pytest
from datetime import datetime

from src.domain.entities.tactical_report import TacticalReport
from src.domain.value_objects.report_section import ReportSection, ContentType


def test_create_report():
    """Test creating a tactical report."""
    report = TacticalReport(
        report_id="r123",
        match_id="m123",
        team_id="home",
        title="Test Report"
    )
    
    assert report.report_id == "r123"
    assert report.match_id == "m123"
    assert report.team_id == "home"
    assert report.title == "Test Report"
    assert isinstance(report.created_at, datetime)
    assert len(report.sections) == 0


def test_add_section():
    """Test adding sections to a report."""
    report = TacticalReport(
        report_id="r123",
        match_id="m123",
        team_id="home",
        title="Test Report"
    )
    
    section = ReportSection(
        title="Summary",
        content_type=ContentType.TEXT,
        content="Match summary text",
        order=1
    )
    
    report.add_section(section)
    
    assert report.section_count() == 1
    assert report.sections[0].title == "Summary"


def test_sections_sorted_by_order():
    """Test that sections are sorted by order."""
    report = TacticalReport(
        report_id="r123",
        match_id="m123",
        team_id="home",
        title="Test Report"
    )
    
    # Add out of order
    report.add_section(ReportSection("Third", ContentType.TEXT, "3", order=3))
    report.add_section(ReportSection("First", ContentType.TEXT, "1", order=1))
    report.add_section(ReportSection("Second", ContentType.TEXT, "2", order=2))
    
    assert report.sections[0].title == "First"
    assert report.sections[1].title == "Second"
    assert report.sections[2].title == "Third"


def test_get_sections_by_type():
    """Test filtering sections by type."""
    report = TacticalReport(
        report_id="r123",
        match_id="m123",
        team_id="home",
        title="Test Report"
    )
    
    report.add_section(ReportSection("Text 1", ContentType.TEXT, "text", order=1))
    report.add_section(ReportSection("Chart 1", ContentType.CHART, b"png", order=2))
    report.add_section(ReportSection("Text 2", ContentType.TEXT, "text", order=3))
    
    text_sections = report.get_sections_by_type(ContentType.TEXT)
    chart_sections = report.get_sections_by_type(ContentType.CHART)
    
    assert len(text_sections) == 2
    assert len(chart_sections) == 1


def test_to_json():
    """Test JSON export."""
    report = TacticalReport(
        report_id="r123",
        match_id="m123",
        team_id="home",
        title="Test Report"
    )
    
    report.add_section(ReportSection("Summary", ContentType.TEXT, "test", order=1))
    
    json_str = report.to_json()
    
    assert "r123" in json_str
    assert "m123" in json_str
    assert "Summary" in json_str
