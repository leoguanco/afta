import pytest
import os
from unittest.mock import patch
from src.infrastructure.di.container import Container
from src.infrastructure.db.repositories.postgres_match_repo import PostgresMatchRepo
from src.infrastructure.adapters.crewai_adapter import CrewAIAdapter

@patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test", "LLM_PROVIDER": "openai"})
def test_container_singletons():
    """Verify that container returns singletons."""
    # Reset container state if needed (though pytest runs usually separate, manual reset is safer if order matters)
    Container._crewai_adapter = None
    
    # Match Repo
    repo1 = Container.get_match_repo()
    repo2 = Container.get_match_repo()
    assert repo1 is repo2
    assert isinstance(repo1, PostgresMatchRepo)
    
    # Adapter
    adapter1 = Container.get_crewai_adapter()
    adapter2 = Container.get_crewai_adapter()
    assert adapter1 is adapter2
    assert isinstance(adapter1, CrewAIAdapter)

def test_container_injection():
    """Verify that dependencies are correctly injected."""
    service = Container.get_match_context_service()
    
    # Check if the service has the same repo instance as the container
    assert service.match_repo is Container.get_match_repo()
