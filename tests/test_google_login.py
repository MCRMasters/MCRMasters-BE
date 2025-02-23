from fastapi import status
from httpx import AsyncClient, HTTPStatusError, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession


async def test_google_login_url(client: AsyncClient):
    response = await client.get("/api/v1/auth/login/google")

    assert response.status_code == status.HTTP_200_OK
    assert "auth_url" in response.json()
    assert "accounts.google.com" in response.json()["auth_url"]


async def test_google_callback_success(
    client: AsyncClient,
    mocker,
    mock_session: AsyncSession,
    mock_google_responses: dict,
):
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

    async_client_context = mocker.AsyncMock()
    async_client_context.__aenter__.return_value = mock_client
    async_client_context.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=async_client_context)

    mock_result = mocker.Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    response = await client.get("/api/v1/auth/login/google/callback?code=test_code")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["is_new_user"] is True
    assert data["token_type"] == "bearer"


async def test_google_callback_token_error(
    client: AsyncClient,
    mocker,
    mock_session: AsyncSession,
):
    request = Request("POST", "https://oauth2.googleapis.com/token")
    response = Response(400, request=request)

    mock_httpx_post = mocker.patch(
        "httpx.AsyncClient.post",
        side_effect=HTTPStatusError(
            "Token request failed",
            request=request,
            response=response,
        ),
    )

    response = await client.get("/api/v1/auth/login/google/callback?code=invalid_code")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Failed to get token from Google"

    mock_httpx_post.assert_called_once()


async def test_google_callback_userinfo_error(
    client: AsyncClient,
    mocker,
    mock_session: AsyncSession,
    mock_google_responses: dict,
):
    mock_token_response = mocker.Mock()
    mock_token_response.json.return_value = mock_google_responses["token_response"]
    mock_token_response.raise_for_status.return_value = None

    userinfo_request = Request("GET", "https://www.googleapis.com/oauth2/v2/userinfo")
    userinfo_response = Response(400, request=userinfo_request)

    mock_http_error = HTTPStatusError(
        "Failed to get user info",
        request=userinfo_request,
        response=userinfo_response,
    )

    mock_client = mocker.AsyncMock()
    mock_client.post.return_value = mock_token_response
    mock_client.get.side_effect = mock_http_error

    async_client_context = mocker.AsyncMock()
    async_client_context.__aenter__.return_value = mock_client
    async_client_context.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=async_client_context)

    response = await client.get("/api/v1/auth/login/google/callback?code=test_code")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Failed to get token from Google"

    mock_client.post.assert_called_once()
    mock_client.get.assert_called_once()
