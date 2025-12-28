"""
CeleryAnalysisDispatcher - Infrastructure Adapter

Implements AnalysisPort for asynchronous dispatch via Celery.
"""
from src.domain.ports.analysis_port import AnalysisPort
from src.infrastructure.worker.celery_app import celery_app

class CeleryAnalysisDispatcher(AnalysisPort):
    """
    Adapter to dispatch analysis jobs to Celery workers.
    """
    
    def run_analysis(self, match_id: str, query: str, match_context: str = "") -> str:
        """Synchronous run not supported by this dispatcher."""
        raise NotImplementedError("CeleryDispatcher only supports async dispatch.")
        
    def dispatch_analysis(self, match_id: str, query: str) -> str:
        """
        Dispatch the run_crewai_analysis_task to Celery.
        """
        # Using string name to resolve task
        task = celery_app.send_task(
            'src.infrastructure.worker.tasks.crewai_tasks.run_crewai_analysis_task',
            args=[match_id, query]
        )
        return task.id
