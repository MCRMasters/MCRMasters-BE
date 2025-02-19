from asyncio import get_event_loop_policy

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from app.core.config import get_test_settings
from app.db.session import get_session
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """테스트 환경 설정"""
    load_dotenv(".env.test", override=True)
    yield
    load_dotenv(".env", override=True)


@pytest.fixture(scope="session")
def event_loop_policy():
    return get_event_loop_policy()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """테스트 DB 엔진 설정"""
    test_settings = get_test_settings()
    engine = create_async_engine(
        test_settings.database_uri,
        echo=True,
        future=True,
        poolclass=NullPool,
    )

    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncSession:
    """테스트용 DB 세션"""
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """테스트 클라이언트"""
    app.dependency_overrides[get_session] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        try:
            yield ac
        finally:
            app.dependency_overrides.clear()
