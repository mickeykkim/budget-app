"""
Database methods
"""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=_engine, class_=Session
)


def get_engine() -> Engine:
    """Returns engine for SQLAlchemy models."""
    return _engine
