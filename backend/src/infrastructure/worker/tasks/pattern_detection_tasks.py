"""
Pattern Detection Tasks - Infrastructure Layer

Celery tasks for asynchronous pattern detection.
"""
from typing import Optional, Dict, Any, List

from celery import shared_task

from src.application.use_cases.pattern_detector import PatternDetector
from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
from src.infrastructure.logging import get_logger
from src.infrastructure.ml.sklearn_pattern_detector import SklearnPatternDetector

logger = get_logger(__name__)


@shared_task(name="detect_tactical_patterns")
def detect_patterns_task(
    match_id: str,
    team_id: str = "home",
    n_clusters: int = 8
) -> Dict[str, Any]:
    """
    Detect tactical patterns asynchronously.
    
    Args:
        match_id: Match identifier
        team_id: Team perspective
        n_clusters: Number of pattern clusters
        
    Returns:
        Dictionary with pattern detection results
    """
    logger.info(f"Starting pattern detection for match {match_id}")
    
    try:
        # Create dependencies
        detector = SklearnPatternDetector(algorithm="kmeans")
        match_repo = PostgresMatchRepo()
        
        # Create Use Case
        use_case = PatternDetector(
            detector=detector,
            match_repository=match_repo
        )
        
        # Execute
        result = use_case.execute(
            match_id=match_id,
            team_id=team_id,
            n_clusters=n_clusters
        )
        
        logger.info(f"Pattern detection complete: {result.pattern_count} patterns found")
        
        return {
            "status": "success",
            "match_id": result.match_id,
            "team_id": result.team_id,
            "pattern_count": result.pattern_count,
            "sequence_count": result.sequence_count,
            "patterns": [p.to_dict() for p in result.patterns]
        }
        
    except Exception as e:
        logger.error(f"Pattern detection failed: {e}")
        raise

