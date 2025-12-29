"""
PDFGenerator - Infrastructure Layer

Implements ReportGeneratorPort using WeasyPrint for PDF generation.
"""
import base64
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader

from src.domain.entities.tactical_report import TacticalReport
from src.domain.ports.report_generator_port import ReportGeneratorPort
from src.domain.value_objects.report_section import ContentType


# Template directory
TEMPLATE_DIR = Path(__file__).parent / "templates"


class WeasyPrintReportGenerator(ReportGeneratorPort):
    """
    PDF report generator using WeasyPrint.
    
    Renders HTML templates with Jinja2 and converts to PDF.
    """
    
    def __init__(self):
        """Initialize the generator with Jinja2 environment."""
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=True
        )
    
    def generate_pdf(self, report: TacticalReport) -> bytes:
        """
        Generate PDF from TacticalReport.
        
        Args:
            report: TacticalReport entity
            
        Returns:
            PDF bytes
        """
        # Lazy import to avoid loading weasyprint in API
        from weasyprint import HTML
        
        # Render HTML
        html_content = self._render_html(report)
        
        # Convert to PDF
        pdf_bytes = HTML(string=html_content).write_pdf()
        
        return pdf_bytes
    
    def generate_json(self, report: TacticalReport) -> str:
        """
        Generate JSON from TacticalReport.
        
        Uses the entity's built-in JSON export.
        """
        return report.to_json()
    
    def _render_html(self, report: TacticalReport) -> str:
        """Render HTML template with report data."""
        template = self.env.get_template("tactical_report.html")
        
        # Prepare sections for template
        sections_data = []
        for section in report.sections:
            section_dict = {
                "title": section.title,
                "content_type": section.content_type.value,
                "description": section.description,
                "order": section.order,
            }
            
            # Handle different content types
            if section.content_type == ContentType.CHART:
                # Charts should be base64 encoded PNG
                if isinstance(section.content, bytes):
                    section_dict["content"] = base64.b64encode(section.content).decode('utf-8')
                else:
                    section_dict["content"] = section.content
            else:
                section_dict["content"] = section.content
            
            sections_data.append(section_dict)
        
        return template.render(
            title=report.title,
            match_id=report.match_id,
            team_id=report.team_id,
            report_id=report.report_id,
            created_at=report.created_at.strftime("%Y-%m-%d %H:%M"),
            sections=sections_data,
            metadata=report.metadata
        )


class SimplePDFGenerator(ReportGeneratorPort):
    """
    Fallback PDF generator using reportlab (pure Python, no system deps).
    
    Use this if WeasyPrint system dependencies are not available.
    """
    
    def generate_pdf(self, report: TacticalReport) -> bytes:
        """Generate a simple PDF using reportlab."""
        # Lazy import
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet
        import io
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(Paragraph(report.title, styles['Title']))
        story.append(Spacer(1, 20))
        
        # Metadata
        meta_text = f"Match: {report.match_id} | Team: {report.team_id} | {report.created_at.strftime('%Y-%m-%d')}"
        story.append(Paragraph(meta_text, styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Sections
        for section in report.sections:
            story.append(Paragraph(section.title, styles['Heading2']))
            story.append(Spacer(1, 10))
            
            if section.content_type == ContentType.TEXT:
                story.append(Paragraph(str(section.content), styles['Normal']))
            elif section.content_type == ContentType.AI_ANALYSIS:
                story.append(Paragraph(str(section.content), styles['Normal']))
            elif section.content_type == ContentType.METRICS:
                metrics_text = "<br/>".join([f"{k}: {v}" for k, v in section.content.items()])
                story.append(Paragraph(metrics_text, styles['Normal']))
            # Charts would need special handling with reportlab
            
            story.append(Spacer(1, 20))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_json(self, report: TacticalReport) -> str:
        """Generate JSON from TacticalReport."""
        return report.to_json()
