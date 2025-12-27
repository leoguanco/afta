"""
StatsBomb Adapter.

Infrastructure adapter that implements MatchRepository using statsbombpy.
"""

from typing import Optional
import statsbombpy as sb

from src.domain.entities.event import Event, EventType
from src.domain.entities.match import Match
from src.domain.ports.match_repository import MatchRepository
from src.domain.value_objects.coordinates import Coordinates


# Mapping from StatsBomb event types to our domain EventType
STATSBOMB_EVENT_MAP = {
    "Pass": EventType.PASS,
    "Shot": EventType.SHOT,
    "Carry": EventType.CARRY,
    "Dribble": EventType.DRIBBLE,
    "Tackle": EventType.TACKLE,
    "Interception": EventType.INTERCEPTION,
    "Clearance": EventType.CLEARANCE,
    "Foul Committed": EventType.FOUL,
    "Goal Keeper": EventType.CLEARANCE,  # Simplified mapping
}


class StatsBombAdapter(MatchRepository):
    """
    Adapter for StatsBomb open data.

    Fetches match data from StatsBomb API and transforms to Domain entities.
    """

    def get_match(self, match_id: str, source: str) -> Optional[Match]:
        """
        Fetch a match from StatsBomb open data.

        Args:
            match_id: StatsBomb match ID.
            source: Should be "statsbomb" (ignored here).

        Returns:
            Match aggregate with normalized events.
        """
        try:
            # Fetch events from StatsBomb
            events_df = sb.events(match_id=int(match_id))

            if events_df.empty:
                return None

            # Create Match aggregate
            match = Match(
                match_id=match_id,
                home_team_id=str(events_df["team"].iloc[0]),
                away_team_id=str(events_df["team"].unique()[-1]),
            )

            # Transform each event
            for _, row in events_df.iterrows():
                event = self._transform_event(row)
                if event:
                    match.add_event(event)

            return match

        except Exception:
            return None

    def save(self, match: Match) -> None:
        """
        Save is not supported for StatsBomb (read-only source).

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError("StatsBomb is a read-only data source")

    def _transform_event(self, row) -> Optional[Event]:
        """Transform a StatsBomb event row to a Domain Event."""
        event_type_str = row.get("type")

        if event_type_str not in STATSBOMB_EVENT_MAP:
            return None

        # Get location (StatsBomb uses [x, y] format)
        location = row.get("location")
        if location is None or len(location) < 2:
            return None

        # Transform coordinates from StatsBomb (120x80) to Metric (105x68)
        coords = Coordinates.from_statsbomb(location[0], location[1])

        return Event(
            event_id=str(row.get("id", "")),
            event_type=STATSBOMB_EVENT_MAP[event_type_str],
            timestamp=float(row.get("minute", 0) * 60 + row.get("second", 0)),
            coordinates=coords,
            player_id=str(row.get("player_id", "unknown")),
            team_id=str(row.get("team_id", "")),
        )
