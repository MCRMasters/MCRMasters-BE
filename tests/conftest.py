from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """테스트 환경 설정"""
    load_dotenv(".env.test", override=True)
    yield
    load_dotenv(".env", override=True)


@pytest_asyncio.fixture
async def mock_session() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncMock(spec=AsyncSession)

    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()

    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    yield session


@pytest_asyncio.fixture
async def client(mock_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_session] = lambda: mock_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_google_responses():
    return {
        "token_response": {
            "access_token": "mock_access_token",
            "refresh_token": "mock_refresh_token",
            "id_token": "mock_id_token",
            "expires_in": 3600,
        },
        "userinfo_response": {
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/picture.jpg",
        },
    }
