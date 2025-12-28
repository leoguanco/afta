"""
ChromaDB Adapter - Infrastructure Layer

Implements VectorStorePort using ChromaDB for local vector storage.
Uses SentenceTransformers for embeddings (no OpenAI API required).
"""
import os
import logging
from typing import List, Dict, Any, Optional
import uuid

from src.domain.ports.vector_store_port import VectorStorePort, SearchResult

logger = logging.getLogger(__name__)


class ChromaDBAdapter(VectorStorePort):
    """
    ChromaDB implementation of VectorStorePort.
    
    Uses local embeddings via SentenceTransformers for privacy and 
    no API costs. ChromaDB provides persistent vector storage.
    
    Default embedding model: all-MiniLM-L6-v2 (fast, good quality)
    """
    
    def __init__(
        self, 
        collection_name: str = "afta_matches",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize ChromaDB adapter.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory for persistent storage
            embedding_model: SentenceTransformers model name
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        
        # Lazy initialization
        self._client = None
        self._collection = None
        self._embedder = None
    
    def _get_client(self):
        """Lazy load ChromaDB client."""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
                
                self._client = chromadb.Client(Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=self.persist_directory,
                    anonymized_telemetry=False
                ))
                logger.info(f"ChromaDB client initialized at {self.persist_directory}")
            except ImportError:
                logger.warning("ChromaDB not installed, using in-memory fallback")
                import chromadb
                self._client = chromadb.Client()
                
        return self._client
    
    def _get_collection(self):
        """Lazy load collection."""
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Using collection: {self.collection_name}")
            
        return self._collection
    
    def _get_embedder(self):
        """Lazy load embedding model."""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer(self.embedding_model)
                logger.info(f"Loaded embedding model: {self.embedding_model}")
            except ImportError:
                logger.error("SentenceTransformers not installed")
                raise RuntimeError(
                    "Please install sentence-transformers: "
                    "pip install sentence-transformers"
                )
                
        return self._embedder
    
    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        embedder = self._get_embedder()
        embeddings = embedder.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def add_documents(
        self, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add documents to ChromaDB with embeddings."""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        # Generate embeddings
        embeddings = self._embed(documents)
        
        # Add to collection
        collection = self._get_collection()
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(documents)} documents to ChromaDB")
        return ids
    
    def query(
        self, 
        query_text: str, 
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Query ChromaDB for similar documents."""
        # Generate query embedding
        query_embedding = self._embed([query_text])[0]
        
        # Query collection
        collection = self._get_collection()
        
        query_kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        
        if filter_metadata:
            query_kwargs["where"] = filter_metadata
        
        results = collection.query(**query_kwargs)
        
        # Convert to SearchResult objects
        search_results = []
        if results and results["ids"] and len(results["ids"][0]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                # Convert distance to similarity score (cosine: 1 - distance)
                distance = results["distances"][0][i] if results["distances"] else 0
                similarity = 1 - distance
                
                search_results.append(SearchResult(
                    document_id=doc_id,
                    content=results["documents"][0][i] if results["documents"] else "",
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                    similarity_score=similarity
                ))
        
        return search_results
    
    def delete_by_metadata(self, metadata_filter: Dict[str, Any]) -> int:
        """Delete documents matching metadata filter."""
        collection = self._get_collection()
        
        # First, find matching documents
        results = collection.get(where=metadata_filter)
        
        if results and results["ids"]:
            collection.delete(ids=results["ids"])
            count = len(results["ids"])
            logger.info(f"Deleted {count} documents from ChromaDB")
            return count
        
        return 0
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        collection = self._get_collection()
        
        return {
            "collection_name": self.collection_name,
            "document_count": collection.count(),
            "persist_directory": self.persist_directory,
            "embedding_model": self.embedding_model
        }
