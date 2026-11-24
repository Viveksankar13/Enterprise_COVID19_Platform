from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create Async Engine with configured pool properties
# Note: we use asyncpg as the dialect driver (via postgresql+asyncpg)
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    echo=False,  # Set to True to debug SQL queries in log
)

# Async Session Factory
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency generator for obtaining an asynchronous database session.
    Automatically handles commit, rollback on exceptions, and closing of the session.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database transaction exception occurred: {e}. Rolling back.")
            await session.rollback()
            raise
        finally:
            await session.close()
