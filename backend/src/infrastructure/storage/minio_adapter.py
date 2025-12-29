"""
MinIO adapter for ObjectStoragePort.

Implements file storage using MinIO (S3-compatible object storage).
"""

import io
import logging
from minio import Minio
from minio.error import S3Error
import pandas as pd
import os

from src.domain.ports.object_storage_port import ObjectStoragePort

logger = logging.getLogger(__name__)


class MinIOAdapter(ObjectStoragePort):
    """
    MinIO implementation of ObjectStoragePort.
    
    Connects to MinIO service and handles Parquet file operations.
    """

    def __init__(
        self,
        endpoint: str = None,
        access_key: str = None,
        secret_key: str = None,
        bucket: str = "tracking-data"
    ):
        """
        Initialize MinIO client.
        
        Args:
            endpoint: MinIO server endpoint (defaults to env var or localhost:9000).
            access_key: MinIO access key (defaults to env var).
            secret_key: MinIO secret key (defaults to env var).
            bucket: Bucket name for storage.
        """
        self.endpoint = endpoint or os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = access_key or os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = secret_key or os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.bucket = bucket

        # Initialize MinIO client
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False  # Use True for HTTPS
        )

        # Ensure bucket exists
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                logger.info(f"Created bucket: {self.bucket}")
        except S3Error as e:
            logger.error(f"Failed to check/create bucket: {e}")
            raise

    def save_parquet(self, key: str, data: pd.DataFrame) -> None:
        """
        Save a DataFrame as a Parquet file to MinIO.
        
        Args:
            key: Storage path/key (e.g., "tracking/match_123.parquet").
            data: DataFrame to serialize and save.
        """
        try:
            # Serialize DataFrame to Parquet bytes
            buffer = io.BytesIO()
            data.to_parquet(buffer, engine='pyarrow', index=False)
            buffer.seek(0)
            
            # Upload to MinIO
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=key,
                data=buffer,
                length=buffer.getbuffer().nbytes,
                content_type="application/octet-stream"
            )
            
            logger.info(f"Saved Parquet file to MinIO: {self.bucket}/{key}")
        except Exception as e:
            logger.error(f"Failed to save Parquet to MinIO: {e}")
            raise

    def get_parquet(self, key: str) -> pd.DataFrame:
        """
        Retrieve a Parquet file from MinIO as a DataFrame.
        
        Args:
            key: Storage path/key.
        
        Returns:
            DataFrame loaded from Parquet file.
        """
        try:
            # Download from MinIO
            response = self.client.get_object(self.bucket, key)
            data = response.read()
            response.close()
            response.release_conn()
            
            # Deserialize Parquet bytes to DataFrame
            buffer = io.BytesIO(data)
            df = pd.read_parquet(buffer, engine='pyarrow')
            
            logger.info(f"Retrieved Parquet file from MinIO: {self.bucket}/{key}")
            return df
        except Exception as e:
            logger.error(f"Failed to retrieve Parquet from MinIO: {e}")
            raise

    def put_object(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
        """
        Store raw bytes in MinIO.
        
        Args:
            key: Storage path/key.
            data: Raw bytes to store.
            content_type: MIME type of the content.
        """
        try:
            buffer = io.BytesIO(data)
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=key,
                data=buffer,
                length=len(data),
                content_type=content_type
            )
            logger.info(f"Stored object in MinIO: {self.bucket}/{key}")
        except Exception as e:
            logger.error(f"Failed to store object in MinIO: {e}")
            raise

    def get_object(self, key: str) -> bytes:
        """
        Retrieve raw bytes from MinIO.
        
        Args:
            key: Storage path/key.
            
        Returns:
            Raw bytes of the object.
        """
        try:
            response = self.client.get_object(self.bucket, key)
            data = response.read()
            response.close()
            response.release_conn()
            logger.info(f"Retrieved object from MinIO: {self.bucket}/{key}")
            return data
        except Exception as e:
            logger.error(f"Failed to retrieve object from MinIO: {e}")
            raise
