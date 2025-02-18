from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import settings
from app.db.session import get_session
from app.main import app


@pytest.fixture(scope="session")
def load_test_env():
    load_dotenv(".env.test", override=True)


@pytest_asyncio.fixture
async def test_engine(load_test_env):  # noqa: ARG001
    """
    비동기 데이터베이스 엔진 생성 픽스처
    """
    engine = create_async_engine(
        settings.database_uri,
        echo=True,
        future=True,
        pool_pre_ping=True,
    )
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def create_test_db(test_engine):
    """
    테스트 데이터베이스 생성 및 정리 픽스처
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    비동기 데이터베이스 세션 픽스처
    """
    session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with session_maker() as session:
        yield session
        await session.rollback()
        await session.close()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    비동기 테스트 클라이언트 픽스처
    """

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        yield ac
