"""
Dependency Injection Container - Infrastructure Layer

Simple DI container to manage singleton dependencies.
"""
from typing import Optional

from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
from src.infrastructure.db.repositories.postgres_metrics_repo import PostgresMetricsRepository
from src.application.services.match_context_service import MatchContextService
from src.infrastructure.adapters.crewai_adapter import CrewAIAdapter


class Container:
    """
    Simple Dependency Injection Container.
    
    Provides lazy-loaded singleton instances of infrastructure and application components.
    """
    _match_repo: Optional[PostgresMatchRepo] = None
    _metrics_repo: Optional[PostgresMetricsRepository] = None
    _match_context_service: Optional[MatchContextService] = None
    _crewai_adapter: Optional[CrewAIAdapter] = None

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
    def get_match_context_service(cls) -> MatchContextService:
        """Get or create MatchContextService instance with injected repos."""
        if cls._match_context_service is None:
            cls._match_context_service = MatchContextService(
                cls.get_match_repo(),
                cls.get_metrics_repo()
            )
        return cls._match_context_service

    @classmethod
    def get_crewai_adapter(cls) -> CrewAIAdapter:
        """Get or create CrewAIAdapter instance."""
        if cls._crewai_adapter is None:
            cls._crewai_adapter = CrewAIAdapter()
        return cls._crewai_adapter
