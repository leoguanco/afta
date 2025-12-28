"""
PostgresPhaseRepository - Infrastructure Layer

PostgreSQL implementation of PhaseRepository using SQLAlchemy.
"""
from typing import List, Optional
import logging

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.domain.ports.phase_repository import PhaseRepository
from src.domain.entities.phase_sequence import PhaseSequence, PhaseTransition, FramePhase
from src.domain.value_objects.game_phase import GamePhase
from src.infrastructure.db.database import SessionLocal
from src.infrastructure.db.models import (
    PhaseSequenceModel,
    FramePhaseModel,
    PhaseTransitionModel,
    MatchModel
)

logger = logging.getLogger(__name__)


class PostgresPhaseRepository(PhaseRepository):
    """
    PostgreSQL implementation for phase storage.
    
    Uses SQLAlchemy ORM for database operations.
    Stores phase sequences, frame phases, and transitions.
    """
    
    def _get_session(self) -> Session:
        """Get a new database session."""
        return SessionLocal()
    
    def save_phase_sequence(self, sequence: PhaseSequence) -> None:
        """Save phase sequence to PostgreSQL."""
        session = self._get_session()
        try:
            # Check if sequence already exists
            existing = session.query(PhaseSequenceModel).filter(
                and_(
                    PhaseSequenceModel.match_id == sequence.match_id,
                    PhaseSequenceModel.team_id == sequence.team_id
                )
            ).first()
            
            if existing:
                # Delete existing and recreate
                session.delete(existing)
                session.flush()
            
            # Ensure match exists (create placeholder if not)
            match = session.query(MatchModel).filter(
                MatchModel.match_id == sequence.match_id
            ).first()
            
            if not match:
                match = MatchModel(
                    match_id=sequence.match_id,
                    source="phase_classification"
                )
                session.add(match)
                session.flush()
            
            # Create sequence model
            phase_percentages = sequence.get_phase_percentages()
            seq_model = PhaseSequenceModel(
                match_id=sequence.match_id,
                team_id=sequence.team_id,
                fps=sequence.fps,
                total_frames=len(sequence),
                statistics={
                    "phase_percentages": {
                        phase.value: pct for phase, pct in phase_percentages.items()
                    },
                    "transition_count": sequence.get_transition_count(),
                    "dominant_phase": sequence.get_dominant_phase().value
                }
            )
            session.add(seq_model)
            session.flush()
            
            # Add frame phases in batches
            batch_size = 1000
            for i in range(0, len(sequence.frame_phases), batch_size):
                batch = sequence.frame_phases[i:i + batch_size]
                for fp in batch:
                    frame_model = FramePhaseModel(
                        sequence_id=seq_model.id,
                        frame_id=fp.frame_id,
                        phase=fp.phase.value,
                        confidence=fp.confidence
                    )
                    session.add(frame_model)
                session.flush()
            
            # Add transitions
            transitions = sequence.calculate_phase_transitions()
            for t in transitions:
                trans_model = PhaseTransitionModel(
                    sequence_id=seq_model.id,
                    frame_id=t.frame_id,
                    timestamp=t.timestamp,
                    from_phase=t.from_phase.value,
                    to_phase=t.to_phase.value
                )
                session.add(trans_model)
            
            session.commit()
            logger.info(f"Saved phase sequence for match {sequence.match_id}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save phase sequence: {e}")
            raise
        finally:
            session.close()
    
    def get_phase_sequence(
        self, 
        match_id: str, 
        team_id: str = "home"
    ) -> Optional[PhaseSequence]:
        """Get phase sequence from PostgreSQL."""
        session = self._get_session()
        try:
            seq_model = session.query(PhaseSequenceModel).filter(
                and_(
                    PhaseSequenceModel.match_id == match_id,
                    PhaseSequenceModel.team_id == team_id
                )
            ).first()
            
            if not seq_model:
                return None
            
            # Build domain entity
            sequence = PhaseSequence(
                match_id=match_id,
                team_id=team_id,
                fps=seq_model.fps
            )
            
            # Load frame phases
            frame_models = session.query(FramePhaseModel).filter(
                FramePhaseModel.sequence_id == seq_model.id
            ).order_by(FramePhaseModel.frame_id).all()
            
            for fm in frame_models:
                sequence.add_frame_phase(
                    frame_id=fm.frame_id,
                    phase=GamePhase.from_string(fm.phase),
                    confidence=fm.confidence
                )
            
            return sequence
            
        finally:
            session.close()
    
    def get_phases_in_range(
        self,
        match_id: str,
        team_id: str,
        start_frame: int,
        end_frame: Optional[int]
    ) -> List[dict]:
        """Get phase labels for frame range."""
        session = self._get_session()
        try:
            seq_model = session.query(PhaseSequenceModel).filter(
                and_(
                    PhaseSequenceModel.match_id == match_id,
                    PhaseSequenceModel.team_id == team_id
                )
            ).first()
            
            if not seq_model:
                return []
            
            query = session.query(FramePhaseModel).filter(
                and_(
                    FramePhaseModel.sequence_id == seq_model.id,
                    FramePhaseModel.frame_id >= start_frame
                )
            )
            
            if end_frame is not None:
                query = query.filter(FramePhaseModel.frame_id <= end_frame)
            
            frame_models = query.order_by(FramePhaseModel.frame_id).all()
            
            return [
                {
                    "frame_id": fm.frame_id,
                    "phase": fm.phase,
                    "confidence": fm.confidence
                }
                for fm in frame_models
            ]
            
        finally:
            session.close()
    
    def get_transitions(
        self,
        match_id: str,
        team_id: str
    ) -> List[PhaseTransition]:
        """Get all phase transitions."""
        session = self._get_session()
        try:
            seq_model = session.query(PhaseSequenceModel).filter(
                and_(
                    PhaseSequenceModel.match_id == match_id,
                    PhaseSequenceModel.team_id == team_id
                )
            ).first()
            
            if not seq_model:
                return []
            
            trans_models = session.query(PhaseTransitionModel).filter(
                PhaseTransitionModel.sequence_id == seq_model.id
            ).order_by(PhaseTransitionModel.frame_id).all()
            
            return [
                PhaseTransition(
                    frame_id=tm.frame_id,
                    from_phase=GamePhase.from_string(tm.from_phase),
                    to_phase=GamePhase.from_string(tm.to_phase),
                    timestamp=tm.timestamp
                )
                for tm in trans_models
            ]
            
        finally:
            session.close()
    
    def has_classification(self, match_id: str, team_id: str = "home") -> bool:
        """Check if classification exists."""
        session = self._get_session()
        try:
            count = session.query(PhaseSequenceModel).filter(
                and_(
                    PhaseSequenceModel.match_id == match_id,
                    PhaseSequenceModel.team_id == team_id
                )
            ).count()
            return count > 0
            
        finally:
            session.close()
    
    def delete_phase_sequence(self, match_id: str, team_id: str = "home") -> bool:
        """Delete phase sequence from database."""
        session = self._get_session()
        try:
            seq_model = session.query(PhaseSequenceModel).filter(
                and_(
                    PhaseSequenceModel.match_id == match_id,
                    PhaseSequenceModel.team_id == team_id
                )
            ).first()
            
            if seq_model:
                session.delete(seq_model)
                session.commit()
                return True
            return False
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete phase sequence: {e}")
            raise
        finally:
            session.close()
    
    def get_statistics(self, match_id: str, team_id: str = "home") -> Optional[dict]:
        """Get precomputed statistics without loading all frames."""
        session = self._get_session()
        try:
            seq_model = session.query(PhaseSequenceModel).filter(
                and_(
                    PhaseSequenceModel.match_id == match_id,
                    PhaseSequenceModel.team_id == team_id
                )
            ).first()
            
            if not seq_model:
                return None
            
            return {
                "total_frames": seq_model.total_frames,
                "fps": seq_model.fps,
                **seq_model.statistics
            }
            
        finally:
            session.close()


# Singleton instance for dependency injection
phase_repository = PostgresPhaseRepository()
