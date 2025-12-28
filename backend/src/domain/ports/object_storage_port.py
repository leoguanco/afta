"""
ObjectStoragePort - Domain port for file storage operations.

Defines the contract for storing and retrieving files from object storage.
This is a Domain Port and MUST NOT import any external libraries.
"""

from abc import ABC, abstractmethod
from typing import Any
import pandas as pd


class ObjectStoragePort(ABC):
    """
    Abstract interface for object storage operations.
    
    Concrete implementations will be in the Infrastructure layer (e.g., MinIOAdapter).
    """

    @abstractmethod
    def save_parquet(self, key: str, data: pd.DataFrame) -> None:
        """
        Save a DataFrame as a Parquet file to object storage.
        
        Args:
            key: Storage path/key (e.g., "tracking/match_123.parquet").
            data: DataFrame to serialize and save.
        """
        ...

    @abstractmethod
    def get_parquet(self, key: str) -> pd.DataFrame:
        """
        Retrieve a Parquet file from object storage as a DataFrame.
        
        Args:
            key: Storage path/key.
        
        Returns:
            DataFrame loaded from Parquet file.
        """
        ...
