"""SQLAlchemy engine, declarative base, and request-scoped sessions."""
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import get_settings

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    """Base class inherited by all database models."""

def get_db():
    """Yield and safely close one database session for a request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
