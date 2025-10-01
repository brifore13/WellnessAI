"""
Database connection and session management.
Handles PostgreSQL connections with async SQLAlchemy
"""
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base for models
Base = declarative_base()


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self):
        self.engine = None
        self.session_factory = None

    async def initialize(self) -> None:
        """Initialize database engine and session factory."""
        logger.info("Initializing database connection...")

        # Create async engine
        self.engine = create_async_engine(
            settings.database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            echo=settings.debug,    # Log SQL queries in debug mode
            future=True
        )

        # Create session factory
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        logger.info("Database connection initialized successfully")

    async def close(self) -> None:
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session with automatic cleanup"""
        if not self.session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global database manager instance
database_manager = DatabaseManager()


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    Use with route handlers.
    """
    async with database_manager.get_session() as session:
        yield session


# Database lifecycle events for FastAPI
async def startup_database():
    """Initialize database on app startup."""
    await database_manager.initialize()


async def shutdown_database():
    """Close database connections on app shurtdown."""
    await database_manager.close()
