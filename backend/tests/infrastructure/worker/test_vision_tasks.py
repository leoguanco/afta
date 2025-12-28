"""
Unit tests for Vision Tasks.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from minio.error import S3Error
from src.infrastructure.worker.tasks.vision_tasks import process_video_task

class TestVisionTasks:
    """Test suite for Vision Tasks."""

    @patch('src.infrastructure.worker.tasks.vision_tasks.MinIOAdapter')
    @patch('src.infrastructure.worker.tasks.vision_tasks.YOLODetector')
    @patch('src.infrastructure.worker.tasks.vision_tasks.ByteTrackerAdapter')
    @patch('src.infrastructure.worker.tasks.vision_tasks.cv2.VideoCapture')
    def test_process_video_retry_on_s3_error(self, mock_cap, mock_tracker, mock_detector, mock_minio):
        """Test that the task raises retry on S3Error."""
        # Arrange
        # Mock successful video processing
        mock_cap_instance = Mock()
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.read.side_effect = [(True, "frame"), (False, None)] # One frame then end
        mock_cap.return_value = mock_cap_instance
        
        # Mock MinIO failure with S3Error
        mock_storage = Mock()
        mock_storage.save_parquet.side_effect = S3Error(
            code="InternalError",
            message="MinIO down",
            resource="/bucket",
            request_id="123",
            host_id="1",
            response="error"
        )
        mock_minio.return_value = mock_storage
        
        # Mock Celery retry
        process_video_task.retry = Mock(side_effect=Exception("Retry triggered"))

        # Act & Assert
        with pytest.raises(Exception, match="Retry triggered"):
            process_video_task(video_path="match_123.mp4", output_path="out.parquet")
            
        # Verify retry was called with queue params
        process_video_task.retry.assert_called_once()
        call_kwargs = process_video_task.retry.call_args[1]
        assert isinstance(call_kwargs['exc'], S3Error)
