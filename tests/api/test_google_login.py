import pytest
from fastapi import status
from httpx import AsyncClient, HTTPStatusError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_get_google_login_url(client: AsyncClient):
    response = await client.get("/api/v1/auth/login/google")

    assert response.status_code == status.HTTP_200_OK
    assert "auth_url" in response.json()
    assert "accounts.google.com" in response.json()["auth_url"]


@pytest.mark.asyncio
async def test_google_callback_success(
    client: AsyncClient,
    mocker,
    mock_session: AsyncSession,
    mock_google_responses: dict,
):
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

    response = await client.get("/api/v1/auth/login/google/callback?code=test_code")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["is_new_user"] is True
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_google_callback_error(
    client: AsyncClient,
    mocker,
    mock_session: AsyncSession,
):
    mock_client = mocker.AsyncMock()
    mock_client.post.side_effect = HTTPStatusError(
        "Token request failed",
        request=mocker.Mock(),
        response=mocker.Mock(status_code=400),
    )
    mock_client.__aenter__.return_value = mock_client

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    response = await client.get("/api/v1/auth/login/google/callback?code=invalid_code")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Failed to get token from Google"
