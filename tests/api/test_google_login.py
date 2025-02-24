import pytest
from fastapi import status
from httpx import HTTPStatusError


async def test_get_google_login_url(client):
    response = await client.get("/api/v1/auth/login/google")
    assert response.status_code == status.HTTP_200_OK
    assert "auth_url" in response.json()
    assert "accounts.google.com" in response.json()["auth_url"]


@pytest.mark.asyncio
async def test_google_callback_success(
    client,
    mock_google_client,
    mock_session,
):
    response = await client.get("/api/v1/auth/login/google/callback?code=test_code")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["is_new_user"] is True
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_google_callback_error(client, mocker):
    mocker.patch(
        "httpx.AsyncClient.post",
        side_effect=HTTPStatusError(
            "Token request failed",
            request=mocker.Mock(),
            response=mocker.Mock(status_code=400),
        ),
    )
    response = await client.get("/api/v1/auth/login/google/callback?code=invalid_code")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Failed to get token from Google"
