"""
Test VideoCalibrator Use Case.
"""
import pytest
from unittest.mock import Mock

from src.application.use_cases.video_calibrator import VideoCalibrator
from src.domain.ports.calibration_port import CalibrationPort

def test_execute():
    # Setup
    mock_dispatcher = Mock(spec=CalibrationPort)
    mock_dispatcher.start_calibration.return_value = "job_calib_1"
    
    use_case = VideoCalibrator(mock_dispatcher)
    keypoints = [{"x": 10, "y": 10}]
    
    # Execute
    result = use_case.execute("video_123", keypoints)
    
    # Verify
    assert result.job_id == "job_calib_1"
    assert result.status == "PENDING"
    mock_dispatcher.start_calibration.assert_called_with("video_123", keypoints)
