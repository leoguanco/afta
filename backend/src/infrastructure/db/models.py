"""
SQLAlchemy ORM Models for Match and Event entities.
"""

from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from src.infrastructure.db.database import Base


class MatchModel(Base):
    """
    SQLAlchemy model for Match aggregate.
    
    Maps to 'matches' table in PostgreSQL.
    """
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String, unique=True, nullable=False, index=True)
    source = Column(String, nullable=False)  # 'statsbomb', 'metrica', etc.
    match_metadata = Column(JSON, nullable=True)  # Additional match metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to events
    events = relationship("EventModel", back_populates="match", cascade="all, delete-orphan")
    # Relationship to phase sequences
    phase_sequences = relationship("PhaseSequenceModel", back_populates="match", cascade="all, delete-orphan")


class EventModel(Base):
    """
    SQLAlchemy model for Event entity.
    
    Maps to 'events' table in PostgreSQL.
    """
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String, ForeignKey("matches.match_id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)  # 'Pass', 'Shot', 'Carry', etc.
    timestamp = Column(Float, nullable=False)  # Seconds from match start
    x = Column(Float, nullable=False)  # Metric coordinates (0-105m)
    y = Column(Float, nullable=False)  # Metric coordinates (0-68m)
    event_metadata = Column(JSON, nullable=True)  # Additional event-specific data
    
    # Relationship to match
    match = relationship("MatchModel", back_populates="events")


class PhaseSequenceModel(Base):
    """
    SQLAlchemy model for PhaseSequence aggregate.
    
    Stores phase classification metadata for a match.
    """
    __tablename__ = "phase_sequences"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String, ForeignKey("matches.match_id"), nullable=False, index=True)
    team_id = Column(String, nullable=False, default="home")  # 'home' or 'away'
    fps = Column(Float, default=25.0)
    total_frames = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Statistics stored as JSON for flexibility
    statistics = Column(JSON, nullable=True)  # phase_percentages, transition_count, dominant_phase
    
    # Relationship to match
    match = relationship("MatchModel", back_populates="phase_sequences")
    # Relationship to frame phases
    frame_phases = relationship("FramePhaseModel", back_populates="sequence", cascade="all, delete-orphan")
    
    # Composite unique constraint
    __table_args__ = (
        Index('ix_phase_sequence_match_team', 'match_id', 'team_id', unique=True),
    )


class FramePhaseModel(Base):
    """
    SQLAlchemy model for individual frame phase classifications.
    
    Stores phase label per frame. For large matches, consider using
    a more efficient storage format (e.g., binary blob, partitioning).
    """
    __tablename__ = "frame_phases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sequence_id = Column(Integer, ForeignKey("phase_sequences.id"), nullable=False, index=True)
    frame_id = Column(Integer, nullable=False)
    phase = Column(String, nullable=False)  # GamePhase value
    confidence = Column(Float, default=1.0)
    
    # Relationship to sequence
    sequence = relationship("PhaseSequenceModel", back_populates="frame_phases")
    
    # Index for efficient frame range queries
    __table_args__ = (
        Index('ix_frame_phase_seq_frame', 'sequence_id', 'frame_id'),
    )


class PhaseTransitionModel(Base):
    """
    SQLAlchemy model for phase transitions (precomputed).
    
    Storing transitions separately enables fast queries without
    computing them from frame phases each time.
    """
    __tablename__ = "phase_transitions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sequence_id = Column(Integer, ForeignKey("phase_sequences.id"), nullable=False, index=True)
    frame_id = Column(Integer, nullable=False)
    timestamp = Column(Float, nullable=False)  # Seconds
    from_phase = Column(String, nullable=False)
    to_phase = Column(String, nullable=False)

