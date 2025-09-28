import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings

class DatabaseManager:
    def __init__(self):
        self.engine = None

    async def connect(self):
        """Initialize database connection pool"""
        self.engine = create_async_engine(
            settings.database_url,
            pool_size=10,
            max_overflow=20,
            echo=settings.debug
        )
        logger.info("Database conenction pool initialized")

    async def disconnect(self):
        """Close database connection pool"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection pool closed")

async def get_database() -> AsyncSession:
    """Fast API dependency for database sessions"""
    async with AsyncSession(database_manager.engine) as session:
        try:
            yield session
        finally:
            await session.close()