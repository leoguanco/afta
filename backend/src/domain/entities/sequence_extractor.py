"""
SequenceExtractor - Domain Layer

Extracts possession sequences from match event data.
"""
from typing import List, Dict, Any
import uuid

from src.domain.entities.possession_sequence import PossessionSequence


class SequenceExtractor:
    """
    Domain Service: Extracts possession sequences from event data.
    
    A possession sequence is defined as continuous ball control by one team,
    ending on turnover, out of play, goal, or half end.
    """
    
    # Minimum events for a valid sequence
    MIN_EVENTS = 3
    
    # Event types that end a possession
    ENDING_EVENTS = {
        "ball_lost", "ball_out", "goal", "half_end",
        "foul_won", "clearance", "interception"
    }
    
    # Event types that indicate team change
    TURNOVER_EVENTS = {"interception", "tackle", "dispossessed", "ball_recovery"}
    
    def extract(
        self,
        events: List[Dict[str, Any]],
        match_id: str
    ) -> List[PossessionSequence]:
        """
        Extract possession sequences from events.
        
        Args:
            events: List of match events (sorted by frame/time)
            match_id: Match identifier
            
        Returns:
            List of PossessionSequence entities
        """
        sequences = []
        current_events = []
        current_team = None
        start_frame = 0
        
        for event in events:
            event_team = event.get("team_id") or event.get("team")
            event_type = (event.get("type") or "").lower()
            frame = event.get("frame_id", 0)
            
            # Check if possession changed
            possession_ended = False
            
            if event_team and event_team != current_team:
                possession_ended = True
            elif event_type in self.ENDING_EVENTS:
                possession_ended = True
            elif event_type in self.TURNOVER_EVENTS:
                possession_ended = True
            
            if possession_ended and current_events:
                # Save current sequence if valid
                if len(current_events) >= self.MIN_EVENTS:
                    seq = self._create_sequence(
                        current_events, match_id, current_team,
                        start_frame, frame
                    )
                    sequences.append(seq)
                
                # Reset for new sequence
                current_events = []
                start_frame = frame
            
            # Add event to current sequence
            current_events.append(event)
            if current_team is None or (event_team and event_team != current_team):
                current_team = event_team
                start_frame = frame
        
        # Don't forget last sequence
        if len(current_events) >= self.MIN_EVENTS:
            last_frame = current_events[-1].get("frame_id", start_frame)
            seq = self._create_sequence(
                current_events, match_id, current_team,
                start_frame, last_frame
            )
            sequences.append(seq)
        
        return sequences
    
    def _create_sequence(
        self,
        events: List[Dict[str, Any]],
        match_id: str,
        team_id: str,
        start_frame: int,
        end_frame: int
    ) -> PossessionSequence:
        """Create a PossessionSequence entity."""
        return PossessionSequence(
            sequence_id=str(uuid.uuid4())[:8],
            match_id=match_id,
            team_id=team_id or "unknown",
            start_frame=start_frame,
            end_frame=end_frame,
            events=list(events)
        )
