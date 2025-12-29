"""
ReportGenerator - Application Layer

Use Case for generating tactical match reports.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from src.domain.entities.tactical_report import TacticalReport
from src.domain.value_objects.report_section import ReportSection, ContentType
from src.domain.ports.report_generator_port import ReportGeneratorPort
from src.domain.ports.metrics_repository import MetricsRepository
from src.domain.ports.analysis_port import AnalysisPort
from src.domain.ports.object_storage_port import ObjectStoragePort


@dataclass
class ReportResult:
    """Result of report generation."""
    report_id: str
    match_id: str
    format: str  # "pdf" or "json"
    content: bytes  # PDF bytes or JSON string as bytes
    filename: str


class ReportGenerator:
    """
    Use Case: Generate Tactical Report.
    
    Orchestrates:
    1. Fetching metrics from repository
    2. Generating visualizations
    3. Running AI analysis
    4. Building PDF/JSON output
    """
    
    def __init__(
        self,
        report_generator: ReportGeneratorPort,
        metrics_repository: Optional[MetricsRepository] = None,
        analysis_port: Optional[AnalysisPort] = None,
        chart_generator: Optional[Any] = None,  # ChartGenerator instance
        object_storage: Optional[ObjectStoragePort] = None
    ):
        """
        Initialize with dependencies.
        
        Args:
            report_generator: Port for PDF/JSON generation
            metrics_repository: Optional metrics fetching
            analysis_port: Optional AI analysis
            chart_generator: Optional chart generation
            object_storage: Optional object storage for tracking data
        """
        self.report_generator = report_generator
        self.metrics_repository = metrics_repository
        self.analysis_port = analysis_port
        self.chart_generator = chart_generator
        self.object_storage = object_storage
    
    def execute(
        self,
        match_id: str,
        team_id: str = "home",
        output_format: str = "pdf",
        include_ai_analysis: bool = True,
        include_charts: bool = True,
        title: Optional[str] = None
    ) -> ReportResult:
        """
        Generate a tactical report.
        
        Args:
            match_id: Match identifier
            team_id: Team perspective
            output_format: "pdf" or "json"
            include_ai_analysis: Whether to include AI narrative
            include_charts: Whether to include visualizations
            title: Optional custom title
            
        Returns:
            ReportResult with generated content
        """
        report_id = str(uuid.uuid4())[:8]
        report_title = title or f"Tactical Report - Match {match_id}"
        
        # Create report entity
        report = TacticalReport(
            report_id=report_id,
            match_id=match_id,
            team_id=team_id,
            title=report_title,
            metadata={
                "generated_by": "AFTA",
                "format": output_format
            }
        )
        
        # Add summary section
        report.add_section(ReportSection(
            title="Executive Summary",
            content_type=ContentType.TEXT,
            content=f"Tactical analysis report for match {match_id} from {team_id} perspective.",
            order=1
        ))
        
        # Add metrics if available
        if self.metrics_repository:
            metrics = self._fetch_metrics(match_id, team_id)
            if metrics:
                report.add_section(ReportSection(
                    title="Key Metrics",
                    content_type=ContentType.METRICS,
                    content=metrics,
                    order=2
                ))
        
        # Add charts if available and requested
        if include_charts and self.chart_generator:
            chart_sections = self._generate_charts(match_id, team_id)
            for i, section in enumerate(chart_sections):
                section_with_order = ReportSection(
                    title=section.title,
                    content_type=section.content_type,
                    content=section.content,
                    description=section.description,
                    order=10 + i
                )
                report.add_section(section_with_order)
        
        # Add AI analysis if available and requested
        if include_ai_analysis and self.analysis_port:
            ai_content = self._get_ai_analysis(match_id, team_id)
            if ai_content:
                report.add_section(ReportSection(
                    title="AI Tactical Analysis",
                    content_type=ContentType.AI_ANALYSIS,
                    content=ai_content,
                    order=100
                ))
        
        # Generate output
        if output_format == "pdf":
            content = self.report_generator.generate_pdf(report)
            filename = f"report_{match_id}_{report_id}.pdf"
        else:
            content = self.report_generator.generate_json(report).encode('utf-8')
            filename = f"report_{match_id}_{report_id}.json"
        
        return ReportResult(
            report_id=report_id,
            match_id=match_id,
            format=output_format,
            content=content,
            filename=filename
        )
    
    def _fetch_metrics(self, match_id: str, team_id: str) -> Dict[str, Any]:
        """
        Fetch metrics from repository.
        
        Retrieves aggregated match summary and formats for display.
        """
        if not self.metrics_repository:
            return {}
        
        try:
            # Get aggregated summary
            summary = self.metrics_repository.get_match_summary(match_id)
            
            # Get PPDA for the team
            ppda_data = self.metrics_repository.get_ppda(match_id, team_id)
            
            # Get physical stats to calculate averages
            physical_stats = self.metrics_repository.get_physical_stats(match_id, team_id)
            
            # Calculate additional metrics
            avg_distance_per_player = 0
            if physical_stats and summary.get("players_tracked", 0) > 0:
                avg_distance_per_player = summary["total_distance_km"] / summary["players_tracked"]
            
            return {
                "total_distance": f"{summary.get('total_distance_km', 0):.1f} km",
                "max_speed": f"{summary.get('max_speed_kmh', 0):.1f} km/h",
                "total_sprints": str(summary.get("total_sprints", 0)),
                "players_tracked": str(summary.get("players_tracked", 0)),
                "avg_distance_per_player": f"{avg_distance_per_player:.2f} km",
                "ppda": f"{ppda_data.get('ppda', 0):.2f}" if ppda_data else "N/A",
                "defensive_actions": str(ppda_data.get("defensive_actions", 0)) if ppda_data else "N/A"
            }
        except Exception as e:
            # Return empty on error, let report continue
            return {"error": f"Failed to fetch metrics: {str(e)}"}
    
    def _generate_charts(self, match_id: str, team_id: str) -> List[ReportSection]:
        """
        Generate chart sections using ChartGenerator.
        
        Creates visualizations from tracking data.
        """
        sections = []
        
        if not self.chart_generator:
            return sections
        
        if not self.object_storage:
            return sections
        
        try:
            # Load tracking data from injected storage port
            try:
                tracking_df = self.object_storage.get_parquet(f"tracking/{match_id}.parquet")
            except Exception:
                # No tracking data available
                return sections
            
            # Extract positions for heatmap
            team_filter = tracking_df['team'] == team_id if 'team' in tracking_df.columns else True
            team_data = tracking_df[team_filter] if isinstance(team_filter, bool) is False else tracking_df
            
            if 'x' in team_data.columns and 'y' in team_data.columns:
                positions = list(zip(team_data['x'].tolist(), team_data['y'].tolist()))
                
                # Generate team heatmap
                heatmap_bytes = self.chart_generator.generate_heatmap(
                    positions=positions[:1000],  # Limit for performance
                    title=f"{team_id.title()} Team Heatmap"
                )
                
                sections.append(ReportSection(
                    title="Team Heatmap",
                    content_type=ContentType.CHART,
                    content=heatmap_bytes,
                    description="Player position density across the pitch"
                ))
            
            # Extract frame for pitch control visualization
            first_frame = tracking_df[tracking_df['frame_id'] == tracking_df['frame_id'].min()] if 'frame_id' in tracking_df.columns else None
            
            if first_frame is not None and len(first_frame) > 0:
                home_positions = []
                away_positions = []
                
                for _, row in first_frame.iterrows():
                    if 'x' in row and 'y' in row:
                        pos = (row['x'], row['y'])
                        if row.get('team') == 'home':
                            home_positions.append(pos)
                        else:
                            away_positions.append(pos)
                
                if home_positions or away_positions:
                    pitch_control_bytes = self.chart_generator.generate_pitch_control_frame(
                        home_positions=home_positions,
                        away_positions=away_positions,
                        title="Starting Formation"
                    )
                    
                    sections.append(ReportSection(
                        title="Starting Formation",
                        content_type=ContentType.CHART,
                        content=pitch_control_bytes,
                        description="Player positions at match start"
                    ))
            
        except Exception as e:
            # Log but don't fail report generation
            pass
        
        return sections
    
    def _get_ai_analysis(self, match_id: str, team_id: str) -> Optional[str]:
        """Get AI tactical analysis."""
        if not self.analysis_port:
            return None
        
        try:
            query = f"Provide a tactical summary for {team_id} team in match {match_id}"
            return self.analysis_port.run_analysis(match_id, query)
        except Exception:
            return "AI analysis unavailable."
