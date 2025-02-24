from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.main import app
from app.models.user import User
from app.schemas.google_oauth import GoogleTokenResponse, GoogleUserInfo


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    load_dotenv(".env.test", override=True)
    yield
    load_dotenv(".env", override=True)


@pytest.fixture
def mock_user():
    return User(
        email="test@example.com",
        uid="123456789",
        nickname="",
        last_login=None,
    )


@pytest.fixture
def mock_session(mocker, mock_user):
    session = AsyncMock(spec=AsyncSession)

    mock_result = mocker.Mock()
    mock_result.scalar_one_or_none.return_value = mock_user
    session.execute = AsyncMock(return_value=mock_result)

    return session


@pytest.fixture
def mock_google_client(mocker, mock_google_responses):
    def _create_mock_response(response_data):
        mock_response = mocker.Mock()
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        return mock_response

    mock_client = mocker.AsyncMock()
    mock_client.__aenter__.return_value = mock_client

    mock_client.post.return_value = _create_mock_response(
        mock_google_responses["token_response"],
    )
    mock_client.get.return_value = _create_mock_response(
        mock_google_responses["userinfo_response"],
    )

    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    yield mock_client


@pytest.fixture
def mock_google_responses():
    return {
        "token_response": GoogleTokenResponse(
            access_token="mock_access_token",
            refresh_token="mock_refresh_token",
            id_token="mock_id_token",
            expires_in=3600,
            token_type="Bearer",
            scope="openid email profile",
        ).model_dump(),
        "userinfo_response": GoogleUserInfo(
            email="test@example.com",
            name="Test User",
            picture="https://example.com/picture.jpg",
            verified_email=True,
            locale="en",
        ).model_dump(),
    }


@pytest_asyncio.fixture
async def client(mock_session):
    app.dependency_overrides[get_session] = lambda: mock_session
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()
