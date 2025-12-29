"""
Test ReportGenerator Use Case.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.application.use_cases.report_generator import ReportGenerator, ReportResult
from src.domain.ports.report_generator_port import ReportGeneratorPort
from src.domain.ports.metrics_repository import MetricsRepository
from src.domain.ports.analysis_port import AnalysisPort
from src.domain.value_objects.report_section import ContentType


@pytest.fixture
def mock_report_generator():
    """Mock PDF/JSON generator."""
    gen = Mock(spec=ReportGeneratorPort)
    gen.generate_pdf.return_value = b"PDF_CONTENT"
    gen.generate_json.return_value = '{"report": "json"}'
    return gen


@pytest.fixture
def mock_metrics_repo():
    """Mock metrics repository."""
    repo = Mock(spec=MetricsRepository)
    repo.get_match_summary.return_value = {
        "total_distance_km": 112.5,
        "max_speed_kmh": 34.2,
        "total_sprints": 156,
        "players_tracked": 22,
        "home_ppda": 8.5,
        "away_ppda": 12.3
    }
    repo.get_ppda.return_value = {
        "team_id": "home",
        "ppda": 8.5,
        "defensive_actions": 45,
        "passes_allowed": 382
    }
    repo.get_physical_stats.return_value = [
        {"player_id": "p1", "total_distance": 10.5, "max_speed": 32.1, "sprint_count": 15, "avg_speed": 8.2},
        {"player_id": "p2", "total_distance": 11.2, "max_speed": 34.2, "sprint_count": 18, "avg_speed": 7.9}
    ]
    return repo


@pytest.fixture
def mock_analysis_port():
    """Mock AI analysis port."""
    port = Mock(spec=AnalysisPort)
    port.run_analysis.return_value = "The team showed strong defensive organization."
    return port


class TestReportGenerator:
    
    def test_execute_pdf(self, mock_report_generator):
        """Test basic PDF generation."""
        use_case = ReportGenerator(report_generator=mock_report_generator)
        
        result = use_case.execute("match_123", output_format="pdf")
        
        assert isinstance(result, ReportResult)
        assert result.match_id == "match_123"
        assert result.format == "pdf"
        assert result.content == b"PDF_CONTENT"
        assert result.filename.endswith(".pdf")
        mock_report_generator.generate_pdf.assert_called_once()
    
    def test_execute_json(self, mock_report_generator):
        """Test JSON generation."""
        use_case = ReportGenerator(report_generator=mock_report_generator)
        
        result = use_case.execute("match_123", output_format="json")
        
        assert result.format == "json"
        assert result.filename.endswith(".json")
        mock_report_generator.generate_json.assert_called_once()
    
    def test_with_metrics(self, mock_report_generator, mock_metrics_repo):
        """Test report includes metrics when repository provided."""
        use_case = ReportGenerator(
            report_generator=mock_report_generator,
            metrics_repository=mock_metrics_repo
        )
        
        result = use_case.execute("match_123", team_id="home")
        
        # Verify metrics were fetched
        mock_metrics_repo.get_match_summary.assert_called_with("match_123")
        mock_metrics_repo.get_ppda.assert_called_with("match_123", "home")
    
    def test_with_ai_analysis(self, mock_report_generator, mock_analysis_port):
        """Test report includes AI analysis when port provided."""
        use_case = ReportGenerator(
            report_generator=mock_report_generator,
            analysis_port=mock_analysis_port
        )
        
        result = use_case.execute("match_123", include_ai_analysis=True)
        
        mock_analysis_port.run_analysis.assert_called_once()
    
    def test_without_ai_analysis(self, mock_report_generator, mock_analysis_port):
        """Test AI analysis skipped when disabled."""
        use_case = ReportGenerator(
            report_generator=mock_report_generator,
            analysis_port=mock_analysis_port
        )
        
        result = use_case.execute("match_123", include_ai_analysis=False)
        
        mock_analysis_port.run_analysis.assert_not_called()
    
    def test_custom_title(self, mock_report_generator):
        """Test custom title is used."""
        use_case = ReportGenerator(report_generator=mock_report_generator)
        
        result = use_case.execute("match_123", title="Custom Title")
        
        # Verify PDF was generated (title is in the report entity)
        mock_report_generator.generate_pdf.assert_called_once()
        # Check the report passed has the custom title
        call_args = mock_report_generator.generate_pdf.call_args
        report = call_args[0][0]
        assert report.title == "Custom Title"


class TestFetchMetrics:
    
    def test_fetch_metrics_returns_formatted_data(self, mock_report_generator, mock_metrics_repo):
        """Test _fetch_metrics returns properly formatted data."""
        use_case = ReportGenerator(
            report_generator=mock_report_generator,
            metrics_repository=mock_metrics_repo
        )
        
        metrics = use_case._fetch_metrics("match_123", "home")
        
        assert "total_distance" in metrics
        assert "km" in metrics["total_distance"]
        assert "ppda" in metrics
        assert "8.50" in metrics["ppda"]
    
    def test_fetch_metrics_handles_missing_repo(self, mock_report_generator):
        """Test _fetch_metrics returns empty when no repository."""
        use_case = ReportGenerator(report_generator=mock_report_generator)
        
        metrics = use_case._fetch_metrics("match_123", "home")
        
        assert metrics == {}


class TestGenerateCharts:
    
    def test_generate_charts_no_generator(self, mock_report_generator):
        """Test _generate_charts returns empty without generator."""
        use_case = ReportGenerator(report_generator=mock_report_generator)
        
        sections = use_case._generate_charts("match_123", "home")
        
        assert sections == []
    
    def test_generate_charts_with_data(self, mock_report_generator):
        """Test chart generation with tracking data."""
        import pandas as pd
        from src.domain.ports.object_storage_port import ObjectStoragePort
        
        # Mock object storage port
        mock_storage = Mock(spec=ObjectStoragePort)
        mock_storage.get_parquet.return_value = pd.DataFrame({
            'frame_id': [1, 1, 2, 2],
            'team': ['home', 'away', 'home', 'away'],
            'x': [20.0, 80.0, 25.0, 75.0],
            'y': [30.0, 30.0, 35.0, 35.0]
        })
        
        # Mock chart generator
        mock_chart_gen = Mock()
        mock_chart_gen.generate_heatmap.return_value = b"HEATMAP_PNG"
        mock_chart_gen.generate_pitch_control_frame.return_value = b"PITCH_CONTROL_PNG"
        
        use_case = ReportGenerator(
            report_generator=mock_report_generator,
            chart_generator=mock_chart_gen,
            object_storage=mock_storage
        )
        
        sections = use_case._generate_charts("match_123", "home")
        
        assert len(sections) >= 1
        assert any(s.title == "Team Heatmap" for s in sections)
