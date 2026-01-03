"""
RAG Indexing Integration Tests

Tests for the RAG indexing functionality including:
- MatchDataIndexer use case
- ChromaDBAdapter operations
- MatchContextService RAG retrieval
"""
import pytest
from unittest.mock import Mock, MagicMock

from src.application.use_cases.match_data_indexer import MatchDataIndexer, IndexingResult
from src.application.services.match_context_service import MatchContextService
from src.domain.ports.vector_store_port import VectorStorePort, SearchResult


class FakeVectorStore(VectorStorePort):
    """Fake vector store for testing."""
    
    def __init__(self):
        self.documents = []
        self.metadatas = []
        self.ids = []
    
    def add_documents(self, documents, metadatas, ids=None):
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        self.ids.extend(ids)
        return ids
    
    def query(self, query_text, n_results=5, filter_metadata=None):
        # Simple substring search for testing
        results = []
        for i, doc in enumerate(self.documents):
            if filter_metadata:
                # Check if metadata matches filter
                meta = self.metadatas[i]
                if not all(meta.get(k) == v for k, v in filter_metadata.items()):
                    continue
            if query_text.lower() in doc.lower():
                results.append(SearchResult(
                    document_id=self.ids[i],
                    content=doc,
                    metadata=self.metadatas[i],
                    similarity_score=0.9
                ))
        return results[:n_results]
    
    def delete_by_metadata(self, metadata_filter):
        deleted = 0
        new_docs = []
        new_metas = []
        new_ids = []
        for i, meta in enumerate(self.metadatas):
            if all(meta.get(k) == v for k, v in metadata_filter.items()):
                deleted += 1
            else:
                new_docs.append(self.documents[i])
                new_metas.append(meta)
                new_ids.append(self.ids[i])
        self.documents = new_docs
        self.metadatas = new_metas
        self.ids = new_ids
        return deleted
    
    def get_collection_stats(self):
        return {
            "collection_name": "test",
            "document_count": len(self.documents),
            "persist_directory": "/tmp/test"
        }


class TestMatchDataIndexer:
    """Tests for MatchDataIndexer use case."""
    
    def test_index_match_events(self):
        """Test indexing match events."""
        vector_store = FakeVectorStore()
        indexer = MatchDataIndexer(vector_store)
        
        events = [
            {"type": "goal", "player": "Messi", "team": "Argentina", "minute": 45},
            {"type": "shot", "player": "Mbappe", "team": "France", "minute": 60},
        ]
        
        result = indexer.execute(
            match_id="test-match-1",
            match_events=events
        )
        
        assert result.status == "success"
        assert result.documents_indexed == 2
        assert len(vector_store.documents) == 2
    
    def test_index_match_metrics(self):
        """Test indexing match metrics."""
        vector_store = FakeVectorStore()
        indexer = MatchDataIndexer(vector_store)
        
        metrics = {
            "home_ppda": 8.5,
            "away_ppda": 12.3,
            "total_distance": 110.5,
            "possession": {"home": 55, "away": 45}
        }
        
        result = indexer.execute(
            match_id="test-match-2",
            match_metrics=metrics
        )
        
        assert result.status == "success"
        assert result.documents_indexed > 0
    
    def test_index_empty_data(self):
        """Test indexing with no data returns no_documents status."""
        vector_store = FakeVectorStore()
        indexer = MatchDataIndexer(vector_store)
        
        result = indexer.execute(match_id="test-match-3")
        
        assert result.status == "no_documents"
        assert result.documents_indexed == 0


class TestMatchContextServiceRAG:
    """Tests for MatchContextService with RAG retrieval."""
    
    def test_build_context_with_rag(self):
        """Test that RAG results are included in context."""
        # Setup mocks
        mock_match_repo = Mock()
        mock_match_repo.get_match.return_value = None
        
        mock_metrics_repo = Mock()
        mock_metrics_repo.get_physical_stats.return_value = []
        mock_metrics_repo.get_ppda.return_value = None
        
        # Setup vector store with pre-indexed data
        vector_store = FakeVectorStore()
        vector_store.add_documents(
            documents=["Match had high pressing intensity with PPDA of 7.5"],
            metadatas=[{"match_id": "test-match", "type": "metrics"}]
        )
        
        service = MatchContextService(
            mock_match_repo, 
            mock_metrics_repo, 
            vector_store
        )
        
        context = service.build_context("test-match", query="pressing intensity")
        
        assert "Relevant Context (RAG)" in context
        assert "high pressing intensity" in context
    
    def test_build_context_without_query(self):
        """Test that RAG is skipped without query parameter."""
        mock_match_repo = Mock()
        mock_match_repo.get_match.return_value = None
        
        mock_metrics_repo = Mock()
        mock_metrics_repo.get_physical_stats.return_value = []
        mock_metrics_repo.get_ppda.return_value = None
        
        vector_store = FakeVectorStore()
        
        service = MatchContextService(
            mock_match_repo, 
            mock_metrics_repo, 
            vector_store
        )
        
        context = service.build_context("test-match")  # No query
        
        assert "Relevant Context (RAG)" not in context


class TestVectorStoreOperations:
    """Tests for basic vector store operations."""
    
    def test_add_and_query(self):
        """Test adding documents and querying."""
        store = FakeVectorStore()
        
        store.add_documents(
            documents=["High pressing game", "Low block defense"],
            metadatas=[
                {"match_id": "m1", "type": "analysis"},
                {"match_id": "m2", "type": "analysis"}
            ]
        )
        
        results = store.query("pressing")
        
        assert len(results) == 1
        assert "pressing" in results[0].content.lower()
    
    def test_delete_by_metadata(self):
        """Test deleting documents by metadata."""
        store = FakeVectorStore()
        
        store.add_documents(
            documents=["Doc 1", "Doc 2", "Doc 3"],
            metadatas=[
                {"match_id": "m1"},
                {"match_id": "m1"},
                {"match_id": "m2"}
            ]
        )
        
        deleted = store.delete_by_metadata({"match_id": "m1"})
        
        assert deleted == 2
        assert len(store.documents) == 1
        assert store.documents[0] == "Doc 3"
