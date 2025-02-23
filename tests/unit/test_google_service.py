from datetime import UTC, datetime

import pytest
from httpx import HTTPStatusError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.auth.google import GoogleOAuthService


@pytest.mark.asyncio
async def test_get_google_token_success(mocker, mock_google_responses):
    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_google_responses["token_response"]
    mock_response.raise_for_status.return_value = None

    mock_client = mocker.AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    token_response = await GoogleOAuthService.get_google_token("test_code")

    assert token_response.access_token == "mock_access_token"
    assert token_response.refresh_token == "mock_refresh_token"
    mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_get_google_token_failure(mocker):
    mock_client = mocker.AsyncMock()
    mock_client.post.side_effect = HTTPStatusError(
        "Token request failed",
        request=mocker.Mock(),
        response=mocker.Mock(status_code=400),
    )
    mock_client.__aenter__.return_value = mock_client

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    with pytest.raises(HTTPStatusError):
        await GoogleOAuthService.get_google_token("invalid_code")


@pytest.mark.asyncio
async def test_get_user_info_success(mocker, mock_google_responses):
    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_google_responses["userinfo_response"]
    mock_response.raise_for_status.return_value = None

    mock_client = mocker.AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    user_info = await GoogleOAuthService.get_user_info("mock_access_token")

    assert user_info.email == "test@example.com"
    assert user_info.name == "Test User"
    mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_process_google_login_new_user(
    mocker,
    mock_session: AsyncSession,
    mock_google_responses: dict,
):
    before_login = datetime.now(UTC)

    mock_user = User(
        email="test@example.com",
        uid="123456789",
        nickname="",
        last_login=None,
    )

    mock_result = mocker.Mock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result

    mock_token_response = mocker.Mock()
    mock_token_response.json.return_value = mock_google_responses["token_response"]
    mock_token_response.raise_for_status.return_value = None

    mock_userinfo_response = mocker.Mock()
    mock_userinfo_response.json.return_value = mock_google_responses[
        "userinfo_response"
    ]
    mock_userinfo_response.raise_for_status.return_value = None

    mock_client = mocker.AsyncMock()
    mock_client.post.return_value = mock_token_response
    mock_client.get.return_value = mock_userinfo_response
    mock_client.__aenter__.return_value = mock_client

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    login_response = await GoogleOAuthService.process_google_login(
        "test_code",
        mock_session,
    )

    assert login_response.is_new_user is True
    assert "access_token" in login_response.model_dump()
    assert "refresh_token" in login_response.model_dump()
    assert mock_user.last_login is not None
    assert mock_user.last_login >= before_login
    assert mock_user.last_login <= datetime.now(UTC)
