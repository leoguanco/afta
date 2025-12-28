"""
Database Initialization Script.

Creates all tables defined in models.py.
Run with: python -m src.infrastructure.db.init_db
"""
import asyncio
from src.infrastructure.db.database import engine, Base
from src.infrastructure.db.models import (
    MatchModel, 
    EventModel, 
    PhaseSequenceModel, 
    FramePhaseModel, 
    PhaseTransitionModel
)

def init_db():
    """Create database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
