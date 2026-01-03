"""
Dependency Injection Container - Infrastructure Layer

Simple DI container to manage singleton dependencies.
"""
from typing import Optional

from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
from src.infrastructure.db.repositories.postgres_metrics_repo import PostgresMetricsRepository
from src.application.services.match_context_service import MatchContextService
from src.infrastructure.adapters.crewai_adapter import CrewAIAdapter
from src.infrastructure.storage.chroma_adapter import ChromaDBAdapter
from src.application.use_cases.match_data_indexer import MatchDataIndexer
from src.domain.ports.vector_store_port import VectorStorePort


class Container:
    """
    Simple Dependency Injection Container.
    
    Provides lazy-loaded singleton instances of infrastructure and application components.
    """
    _match_repo: Optional[PostgresMatchRepo] = None
    _metrics_repo: Optional[PostgresMetricsRepository] = None
    _match_context_service: Optional[MatchContextService] = None
    _crewai_adapter: Optional[CrewAIAdapter] = None
    _vector_store: Optional[VectorStorePort] = None
    _match_data_indexer: Optional[MatchDataIndexer] = None

    @classmethod
    def get_match_repo(cls) -> PostgresMatchRepo:
        """Get or create PostgresMatchRepo instance."""
        if cls._match_repo is None:
            cls._match_repo = PostgresMatchRepo()
        return cls._match_repo

    @classmethod
    def get_metrics_repo(cls) -> PostgresMetricsRepository:
        """Get or create PostgresMetricsRepository instance."""
        if cls._metrics_repo is None:
            cls._metrics_repo = PostgresMetricsRepository()
        return cls._metrics_repo

    @classmethod
    def get_vector_store(cls) -> VectorStorePort:
        """Get or create VectorStore (ChromaDB) instance."""
        if cls._vector_store is None:
            cls._vector_store = ChromaDBAdapter()
        return cls._vector_store

    @classmethod
    def get_match_data_indexer(cls) -> MatchDataIndexer:
        """Get or create MatchDataIndexer instance."""
        if cls._match_data_indexer is None:
            cls._match_data_indexer = MatchDataIndexer(cls.get_vector_store())
        return cls._match_data_indexer

    @classmethod
    def get_match_context_service(cls) -> MatchContextService:
        """Get or create MatchContextService instance with injected repos and vector store."""
        if cls._match_context_service is None:
            cls._match_context_service = MatchContextService(
                cls.get_match_repo(),
                cls.get_metrics_repo(),
                cls.get_vector_store()
            )
        return cls._match_context_service

    @classmethod
    def get_crewai_adapter(cls) -> CrewAIAdapter:
        """Get or create CrewAIAdapter instance."""
        if cls._crewai_adapter is None:
            cls._crewai_adapter = CrewAIAdapter()
        return cls._crewai_adapter

