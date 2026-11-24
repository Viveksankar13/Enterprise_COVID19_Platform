import asyncio
from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.main import app
from app.database.session import get_db
from app.database.base import Base

# Use a test database suffix to isolate testing transactions
import os
from sqlalchemy.pool import NullPool
postgres_host = os.getenv("POSTGRES_HOST", "localhost")
TEST_DATABASE_URL = f"postgresql+asyncpg://covid_admin:change_me_strong_password@{postgres_host}:5432/covid19_analytics_test"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool
)

test_session_factory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Creates an instance of the default event loop for the test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db() -> AsyncGenerator[None, None]:
    """
    Ensures test tables are created and subsequently dropped after the test session.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a transactional database session fixture for individual test runs.
    Rolls back changes automatically when test completes.
    """
    async with test_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an HTTPX AsyncClient configured to call the FastAPI app.
    Overrides get_db dependency to point to the test database session.
    """
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app) # type: ignore
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
        
    app.dependency_overrides.clear()
