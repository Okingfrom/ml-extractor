"""
Database configuration and session management
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import Generator

# Environment variables with defaults
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://ml_extractor:password@localhost/ml_extractor"
)

# For development, you can use SQLite
if os.getenv("ENVIRONMENT") == "development":
    DATABASE_URL = "sqlite:///./ml_extractor.db"

# Create SQLAlchemy engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        echo=os.getenv("DEBUG", "false").lower() == "true"
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def get_database_session() -> Generator:
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all tables
    """
    from .database import Base
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """
    Drop all tables (use with caution!)
    """
    from .database import Base
    Base.metadata.drop_all(bind=engine)
