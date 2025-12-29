"""
Report Tasks - Infrastructure Layer

Celery tasks for asynchronous report generation.
"""
from celery import shared_task
from typing import Optional, Dict, Any

from src.infrastructure.logging import get_logger

logger = get_logger(__name__)


@shared_task(name="generate_tactical_report")
def generate_tactical_report_task(
    match_id: str,
    team_id: str = "home",
    output_format: str = "pdf",
    include_ai_analysis: bool = True,
    include_charts: bool = True,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a tactical report asynchronously.
    
    Args:
        match_id: Match identifier
        team_id: Team perspective (home/away)
        output_format: pdf or json
        include_ai_analysis: Include AI narrative
        include_charts: Include visualizations
        title: Custom report title
        
    Returns:
        Dictionary with report_id, filename, and storage location
    """
    logger.info(f"Starting report generation for match {match_id}")
    
    try:
        # Import Use Case and dependencies
        from src.application.use_cases.report_generator import ReportGenerator
        from src.infrastructure.reports.pdf_generator import WeasyPrintReportGenerator, SimplePDFGenerator
        from src.infrastructure.storage.minio_adapter import MinIOAdapter
        
        # Try WeasyPrint, fall back to Simple if unavailable
        try:
            report_generator = WeasyPrintReportGenerator()
        except ImportError:
            logger.warning("WeasyPrint not available, using SimplePDFGenerator")
            report_generator = SimplePDFGenerator()
        
        # Create Use Case
        use_case = ReportGenerator(
            report_generator=report_generator,
            # Other dependencies can be injected here
        )
        
        # Execute
        result = use_case.execute(
            match_id=match_id,
            team_id=team_id,
            output_format=output_format,
            include_ai_analysis=include_ai_analysis,
            include_charts=include_charts,
            title=title
        )
        
        # Store in MinIO
        storage = MinIOAdapter()
        storage_key = f"reports/{result.report_id}.{result.format}"
        
        # Use put_object for raw bytes
        storage.put_object(storage_key, result.content)
        
        logger.info(f"Report generated: {result.filename}")
        
        return {
            "status": "success",
            "report_id": result.report_id,
            "match_id": result.match_id,
            "filename": result.filename,
            "format": result.format,
            "storage_key": storage_key
        }
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise
