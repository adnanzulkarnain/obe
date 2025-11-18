"""
Database Module

Manages database connections and sessions using SQLAlchemy.
Following Clean Code: Dependency Injection, Single Responsibility.
"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import Pool

from app.core.config import settings


# Database engine configuration
# Using connection pooling for better performance
engine = create_engine(
    settings.database.get_connection_url(),
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=20,  # Number of connections to maintain
    max_overflow=10,  # Additional connections if pool is exhausted
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=settings.debug,  # Log SQL queries in debug mode
)


# Configure connection pool timeout
@event.listens_for(Pool, "connect")
def set_connection_timeout(dbapi_conn, connection_record):
    """Set statement timeout for PostgreSQL connections."""
    cursor = dbapi_conn.cursor()
    cursor.execute("SET statement_timeout = 30000")  # 30 seconds
    cursor.close()


# Session factory
# Using sessionmaker pattern for clean session management
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for all database models
Base = declarative_base()


def get_database_session() -> Generator[Session, None, None]:
    """
    Dependency injection function for database sessions.

    Yields a database session and ensures it's properly closed.
    This follows the Dependency Injection principle for clean architecture.

    Usage in FastAPI:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_database_session)):
            # Use db here

    Yields:
        Session: SQLAlchemy database session
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class DatabaseManager:
    """
    Manages database operations like initialization and health checks.

    Separated from session management following Single Responsibility Principle.
    """

    @staticmethod
    def initialize_database() -> None:
        """
        Initialize database by creating all tables.

        Note: In production, use Alembic migrations instead.
        This is useful for development and testing.
        """
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def drop_all_tables() -> None:
        """
        Drop all database tables.

        WARNING: Use only in development/testing!
        """
        if settings.is_production():
            raise RuntimeError(
                "Cannot drop tables in production environment!"
            )
        Base.metadata.drop_all(bind=engine)

    @staticmethod
    def check_database_connection() -> bool:
        """
        Check if database connection is healthy.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            with engine.connect() as connection:
                connection.execute("SELECT 1")
            return True
        except Exception:
            return False

    @staticmethod
    def get_connection_info() -> dict:
        """
        Get database connection information.

        Returns:
            dict: Connection details (without sensitive info)
        """
        return {
            "host": settings.database.host,
            "port": settings.database.port,
            "database": settings.database.name,
            "user": settings.database.user,
            "pool_size": engine.pool.size(),
            "checked_out_connections": engine.pool.checkedout()
        }
