"""
MatchRepository Port (Interface).

Defines the contract for fetching and saving Match aggregates.
This is a Domain Port and MUST NOT import any external libraries.
"""

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.match import Match


class MatchRepository(ABC):
    """
    Abstract interface for Match data access.

    Concrete implementations will be in the Infrastructure layer.
    """

    @abstractmethod
    def get_match(self, match_id: str, source: Optional[str] = None) -> Optional[Match]:
        """
        Fetch a match from a data source.

        Args:
            match_id: Unique identifier for the match.
            source: Data source identifier (e.g., "statsbomb", "metrica").

        Returns:
            Match aggregate if found, None otherwise.
        """
        ...

    @abstractmethod
    def save(self, match: Match) -> None:
        """
        Persist a match aggregate.

        Args:
            match: The Match aggregate to save.
        """
        ...
