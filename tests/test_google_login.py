from datetime import UTC, datetime, timedelta

from fastapi import status
from httpx import AsyncClient, HTTPStatusError, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


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
    # 테스트 시작 시간 기록
    before_login = datetime.now(UTC)

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

    # Mock user 객체 설정
    mock_user = User(
        email="test@example.com",
        uid="123456789",
        nickname="",
        last_login=None,
    )
    mock_result = mocker.Mock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result

    response = await client.get("/api/v1/auth/login/google/callback?code=test_code")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["is_new_user"] is True
    assert data["token_type"] == "bearer"

    # last_login이 업데이트되었는지 확인
    assert mock_user.last_login is not None
    assert mock_user.last_login >= before_login
    assert mock_user.last_login <= datetime.now(UTC)


async def test_google_callback_updates_existing_user_last_login(
    client: AsyncClient,
    mocker,
    mock_session: AsyncSession,
    mock_google_responses: dict,
):
    # 이전 로그인 시간 설정
    old_login_time = datetime.now(UTC) - timedelta(days=1)
    existing_user = User(
        email="test@example.com",
        uid="123456789",
        nickname="test_user",
        last_login=old_login_time,
    )

    # Mock 설정
    mock_result = mocker.Mock()
    mock_result.scalar_one_or_none.return_value = existing_user
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

    async_client_context = mocker.AsyncMock()
    async_client_context.__aenter__.return_value = mock_client
    async_client_context.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=async_client_context)

    before_login = datetime.now(UTC)
    response = await client.get("/api/v1/auth/login/google/callback?code=test_code")

    assert response.status_code == status.HTTP_200_OK

    # last_login이 적절히 업데이트되었는지 확인
    assert existing_user.last_login > old_login_time
    assert existing_user.last_login >= before_login
    assert existing_user.last_login <= datetime.now(UTC)
    assert response.json()["is_new_user"] is False


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
