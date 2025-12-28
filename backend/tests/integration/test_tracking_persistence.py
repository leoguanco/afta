"""
Integration tests for Tracking Persistence.
"""

import pytest
import pandas as pd
from minio import Minio
from minio.error import S3Error

from src.infrastructure.storage.minio_adapter import MinIOAdapter


@pytest.fixture
def minio_adapter():
    """Create a MinIOAdapter for testing (requires local Minio running)."""
    adapter = MinIOAdapter(bucket="test-tracking")
    yield adapter
    
    # Cleanup: remove test bucket objects
    try:
        objects = adapter.client.list_objects("test-tracking", recursive=True)
        for obj in objects:
            adapter.client.remove_object("test-tracking", obj.object_name)
    except:
        pass


@pytest.mark.integration
def test_tracking_persistence_flow(minio_adapter):
    """
    Integration test for tracking persistence flow.
    
    Tests:
    1. Create trajectory DataFrame
    2. Save to MinIO as Parquet
    3. Retrieve and verify data
    
    Note: Requires MinIO service running on localhost:9000
    """
    # Arrange
    trajectory_df = pd.DataFrame({
        "frame_id": [1, 2, 3, 4, 5],
        "object_id": [101, 101, 102, 102, 103],
        "x": [10.5, 15.2, 20.1, 25.3, 30.0],
        "y": [5.1, 7.2, 9.3, 11.4, 13.5],
        "confidence": [0.95, 0.92, 0.88, 0.91, 0.87]
    })
    
    # Act - Save
    minio_adapter.save_parquet("tracking/test_match.parquet", trajectory_df)
    
    # Act - Retrieve
    retrieved_df = minio_adapter.get_parquet("tracking/test_match.parquet")
    
    # Assert
    pd.testing.assert_frame_equal(retrieved_df, trajectory_df)


@pytest.mark.integration  
def test_save_and_verify_file_exists(minio_adapter):
    """Test that saved file actually exists in MinIO."""
    # Arrange
    df = pd.DataFrame({"test": [1, 2, 3]})
    key = "tracking/exists_test.parquet"
    
    # Act
    minio_adapter.save_parquet(key, df)
    
    # Assert - Check file exists
    try:
        stat = minio_adapter.client.stat_object("test-tracking", key)
        assert stat.size > 0
    except S3Error:
        pytest.fail("File does not exist in MinIO")
