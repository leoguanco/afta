"""
Vector Store Port - Domain Layer

Defines the interface for vector storage operations (embedding, querying).
Used for RAG (Retrieval-Augmented Generation) in AI analysis.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Value object for vector search result."""
    document_id: str
    content: str
    metadata: Dict[str, Any]
    similarity_score: float


class VectorStorePort(ABC):
    """
    Port interface for vector storage operations.
    
    Used for RAG functionality - storing embeddings of match data
    and retrieving relevant context for AI analysis.
    """
    
    @abstractmethod
    def add_documents(
        self, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of text documents to embed and store
            metadatas: Metadata for each document (match_id, type, etc.)
            ids: Optional explicit IDs for documents
            
        Returns:
            List of document IDs
        """
        pass
    
    @abstractmethod
    def query(
        self, 
        query_text: str, 
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Query the vector store for similar documents.
        
        Args:
            query_text: Text to search for
            n_results: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of SearchResult with similarity scores
        """
        pass
    
    @abstractmethod
    def delete_by_metadata(self, metadata_filter: Dict[str, Any]) -> int:
        """
        Delete documents matching metadata filter.
        
        Args:
            metadata_filter: Metadata conditions for deletion
            
        Returns:
            Number of documents deleted
        """
        pass
    
    @abstractmethod
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector collection.
        
        Returns:
            Dict with document count, collection name, etc.
        """
        pass
