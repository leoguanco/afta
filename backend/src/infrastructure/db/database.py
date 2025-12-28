"""
Database configuration for SQLAlchemy.

Provides engine and session factory for PostgreSQL connection.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://afta_user:afta_pass@localhost:5432/afta_db"
)

# Create engine (using NullPool for Celery workers to avoid connection issues)
engine = create_engine(
    DATABASE_URL.replace("+asyncpg", ""),  # Use psycopg2 for sync operations
    poolclass=NullPool,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_session():
    """
    Get a database session.
    
    Usage:
        with get_session() as session:
            # Use session
            session.commit()
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
