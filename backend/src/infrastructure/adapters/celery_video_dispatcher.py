"""
CeleryVideoDispatcher - Infrastructure Adapter

Implements VideoProcessingPort using Celery tasks.
"""
from src.domain.ports.video_processing_port import VideoProcessingPort
from src.infrastructure.worker.celery_app import celery_app

class CeleryVideoDispatcher(VideoProcessingPort):
    """
    Adapter to dispatch video processing jobs to Celery workers.
    """
    
    def start_processing(
        self, 
        video_path: str, 
        output_path: str,
        mode: str = "full_match"
    ) -> str:
        """
        Dispatch the process_video_task to Celery.
        
        Args:
            video_path: Path to input video
            output_path: Path to output trajectory file
            mode: Processing mode - "full_match" or "highlights"
        """
        # Using string name to resolve task (loose coupling)
        task = celery_app.send_task(
            'src.infrastructure.worker.tasks.vision_tasks.process_video_task',
            args=[video_path, output_path],
            kwargs={'mode': mode}
        )
        return task.id
