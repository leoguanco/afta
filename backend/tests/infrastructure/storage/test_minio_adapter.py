"""
Unit tests for MinIOAdapter.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
import io

from src.infrastructure.storage.minio_adapter import MinIOAdapter


class TestMinIOAdapter:
    """Test suite for MinIOAdapter."""

    @patch('src.infrastructure.storage.minio_adapter.Minio')
    def test_save_parquet(self, mock_minio_class):
        """Test saving a DataFrame as Parquet to MinIO."""
        # Arrange
        mock_client = Mock()
        mock_minio_class.return_value = mock_client
        mock_client.bucket_exists.return_value = True
        
        adapter = MinIOAdapter()
        df = pd.DataFrame({
            "frame_id": [1, 2, 3],
            "object_id": [101, 102, 103],
            "x": [10.0, 20.0, 30.0],
            "y": [15.0, 25.0, 35.0]
        })
        
        # Act
        adapter.save_parquet("tracking/test.parquet", df)
        
        # Assert
        mock_client.put_object.assert_called_once()
        call_args = mock_client.put_object.call_args
        assert call_args[1]['bucket_name'] == "tracking-data"
        assert call_args[1]['object_name'] == "tracking/test.parquet"

    @patch('src.infrastructure.storage.minio_adapter.pd.read_parquet')
    @patch('src.infrastructure.storage.minio_adapter.Minio')
    def test_get_parquet(self, mock_minio_class, mock_read_parquet):
        """Test retrieving a Parquet file from MinIO."""
        # Arrange
        mock_client = Mock()
        mock_minio_class.return_value = mock_client
        mock_client.bucket_exists.return_value = True
        
        # Mock response from MinIO
        mock_response = Mock()
        mock_response.read.return_value = b"fake_parquet_bytes"
        mock_client.get_object.return_value = mock_response
        
        # Mock pandas reading the bytes
        df_expected = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        mock_read_parquet.return_value = df_expected
        
        adapter = MinIOAdapter()
        
        # Act
        df_retrieved = adapter.get_parquet("tracking/test.parquet")
        
        # Assert
        pd.testing.assert_frame_equal(df_retrieved, df_expected)
        mock_client.get_object.assert_called_once_with("tracking-data", "tracking/test.parquet")
        mock_read_parquet.assert_called_once()
