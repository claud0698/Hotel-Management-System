"""
Database configuration and session management
"""

import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment - prefer .env.local for development, fall back to .env
env_local = Path('.env.local')
if env_local.exists():
    load_dotenv(env_local)
else:
    load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./kos.db')

# Create engine and session factory with optimized connection pooling
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_size=20,  # Maximum number of connections to keep in the pool
    max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
    echo=False,  # Set to True for SQL query logging (disable in production)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
