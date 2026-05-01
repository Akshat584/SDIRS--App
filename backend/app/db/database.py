import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from app.core.config import settings

# The database URL for the application from settings
SQLALCHEMY_DATABASE_URL = settings.database_url

# Create the engine based on the URL with connection pooling
if SQLALCHEMY_DATABASE_URL.startswith('sqlite'):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
else:
    # PostgreSQL with connection pooling for production
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=5,              # Base number of connections
        max_overflow=10,          # Additional connections when pool is full
        pool_timeout=30,          # Seconds to wait for a connection
        pool_recycle=1800,        # Recycle connections after 30 minutes
        pool_pre_ping=True        # Verify connections before use
    )

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the declarative base for SQLAlchemy models
Base = declarative_base()

def get_db():
    """
    Dependency to provide a database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
