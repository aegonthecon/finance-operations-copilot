# backend/app/database.py

"""SQLAlchemy database setup for Finance Copilot.
This module creates the engine, a session factory, and a dependency
`get_db` that yields a session for FastAPI routes.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# SQLite database in the project root (relative to this file)
SQLALCHEMY_DATABASE_URL = "sqlite:///./finance.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal is a factory for new Session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

def get_db() -> Session:
    """FastAPI dependency that provides a database session.
    The session is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
