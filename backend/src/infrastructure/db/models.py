"""
SQLAlchemy ORM Models for Match and Event entities.
"""

from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, DateTime
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
    metadata = Column(JSON, nullable=True)  # Additional match metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to events
    events = relationship("EventModel", back_populates="match", cascade="all, delete-orphan")


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
    metadata = Column(JSON, nullable=True)  # Additional event-specific data
    
    # Relationship to match
    match = relationship("MatchModel", back_populates="events")
