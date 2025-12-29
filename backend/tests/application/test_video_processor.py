"""
Test VideoProcessor Use Case.
"""
import pytest
from unittest.mock import Mock

from src.application.use_cases.video_processor import VideoProcessor
from src.domain.ports.video_processing_port import VideoProcessingPort

def test_execute():
    # Setup
    mock_dispatcher = Mock(spec=VideoProcessingPort)
    mock_dispatcher.start_processing.return_value = "job_123"
    
    use_case = VideoProcessor(mock_dispatcher)
    
    # Execute
    result = use_case.execute("/path/to/video.mp4", "/path/to/output.json")
    
    # Verify
    assert result.job_id == "job_123"
    assert result.status == "PENDING"
    mock_dispatcher.start_processing.assert_called_with("/path/to/video.mp4", "/path/to/output.json")
