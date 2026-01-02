"""
Match Context Service - Application Layer

Service for building rich match context strings for AI analysis.
"""
from collections import Counter
from typing import Dict, Any

from src.domain.ports.match_repository import MatchRepository
from src.domain.ports.metrics_repository import MetricsRepository


class MatchContextService:
    """Service to build context strings from match data."""
    
    def __init__(self, match_repo: MatchRepository, metrics_repo: MetricsRepository):
        """
        Initialize with data repositories (ports).
        
        Args:
            match_repo: Repository for match event data
            metrics_repo: Repository for calculated metrics
        """
        self.match_repo = match_repo
        self.metrics_repo = metrics_repo

    def build_context(self, match_id: str) -> str:
        """
        Build a formatted context string for the match.
        
        Args:
            match_id: Match identifier.
            
        Returns:
            Formatted string with match stats and metrics.
        """
        try:
            match = self.match_repo.get_match(match_id, source="statsbomb")
            
            # Build context string
            context_lines = []
            
            if match:
                context_lines.append(f"Match: {match.home_team_id} vs {match.away_team_id}")
                context_lines.append(f"Total Events: {len(match.events)}")
                
                # Count events by type
                event_counts = Counter(event.event_type.value for event in match.events)
                
                context_lines.append("\nEvent Breakdown:")
                for event_type, count in event_counts.most_common():
                    context_lines.append(f"  - {event_type}: {count}")
                
                # Get events by team (if available)
                team_events = {}
                for event in match.events:
                    if event.team_id:
                        if event.team_id not in team_events:
                            team_events[event.team_id] = []
                        team_events[event.team_id].append(event)
                
                if team_events:
                    context_lines.append("\nTeam Statistics:")
                    for team_id, events in team_events.items():
                        context_lines.append(f"  {team_id}: {len(events)} events")
            else:
                context_lines.append(f"Match: {match_id} (Custom Video Upload)")
                context_lines.append("Note: Official event data (StatsBomb) is not available for this match.")
                context_lines.append("Analysis is based on Computer Vision physical metrics only.")
            
            # --- Metrics Enrichment ---
            # --- Metrics Enrichment ---
            
            # Fetch detailed Physical Stats
            physical_stats = self.metrics_repo.get_physical_stats(match_id)
            if physical_stats:
                context_lines.append("\nPhysical Statistics (Computer Vision):")
                # Sort by distance (descending)
                # physical_stats is a list of dicts, so use key access
                sorted_stats = sorted(physical_stats, key=lambda x: x['total_distance'], reverse=True)[:5]
                for p in sorted_stats:
                    context_lines.append(
                        f"  - Player {p['player_id']}: {p['total_distance']:.2f}km run, "
                        f"{p['sprint_count']} sprints, Max Speed: {p['max_speed']:.1f} km/h"
                    )

            # Fetch detailed PPDA
            # Try to get for both teams (assuming we know team IDs or just look for generic)
            # Since we might not know team IDs if match is not in DB, we'll try 'home' and 'away'
            # or rely on what get_ppda returns.
            # PostgresMetricsRepository.get_ppda takes (match_id, team_id).
            # If we don't have team IDs from match events, we might miss them.
            # But the Repo implementation stores them with provided team_ids.
            # Let's try fetching all PPDA stats if possible? The port get_ppda requires team_id.
            # If match object is None (custom video), we might not know team_ids.
            # However, calculate_metrics usually assigns 'home'/'away' or inferred IDs?
            # Let's check how they are saved. Usually 'home' and 'away' strings or numeric IDs.
            
            # For robustness, we check the match object if available
            team_ids = []
            if match:
                team_ids = [match.home_team_id, match.away_team_id]
            else:
                # Fallback to standard side names if custom
                team_ids = ["home", "away", "Home", "Away"]

            seen_teams = set()
            ppda_lines = []
            
            for team_id in team_ids:
                if str(team_id) in seen_teams:
                    continue
                
                ppda_data = self.metrics_repo.get_ppda(match_id, str(team_id))
                if ppda_data:
                    seen_teams.add(str(team_id))
                    ppda_lines.append(f"  - Team {team_id}: PPDA {ppda_data.get('ppda', 'N/A')}")
            
            if ppda_lines:
                context_lines.append("\nPressure Metrics (PPDA):")
                context_lines.extend(ppda_lines)

            if not context_lines:
                 return "No data found for this match (neither events nor metrics)."

            return "\n".join(context_lines)
            
        except Exception as e:
            return f"Error loading match context: {str(e)}"
