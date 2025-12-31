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


class PhysicalStatsModel(Base):
    """
    SQLAlchemy model for player physical statistics.
    
    Stores per-player metrics like distance, speed, sprints.
    """
    __tablename__ = "physical_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String, ForeignKey("matches.match_id"), nullable=False, index=True)
    player_id = Column(String, nullable=False, index=True)
    team_id = Column(String, nullable=True)  # 'home' or 'away'
    total_distance = Column(Float, default=0.0)  # km
    max_speed = Column(Float, default=0.0)  # km/h
    avg_speed = Column(Float, default=0.0)  # km/h
    sprint_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Composite unique constraint (one record per player per match)
    __table_args__ = (
        Index('ix_physical_stats_match_player', 'match_id', 'player_id', unique=True),
    )


class PPDAStatsModel(Base):
    """
    SQLAlchemy model for PPDA (Passes Per Defensive Action) metrics.
    
    Stores per-team tactical pressing intensity.
    """
    __tablename__ = "ppda_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String, ForeignKey("matches.match_id"), nullable=False, index=True)
    team_id = Column(String, nullable=False)  # 'home' or 'away'
    passes_allowed = Column(Integer, default=0)
    defensive_actions = Column(Integer, default=0)
    ppda = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Composite unique constraint (one record per team per match)
    __table_args__ = (
        Index('ix_ppda_stats_match_team', 'match_id', 'team_id', unique=True),
    )


