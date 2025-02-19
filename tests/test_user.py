from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.security import get_password_hash
from app.models.user import User


async def test_successful_user_registration(
    client: AsyncClient,
    db_session: AsyncSession,
):
    """
    성공적인 사용자 등록 테스트
    """
    # Given: 새로운 사용자 정보
    user_data = {
        "username": "testuser",
        "password": "strongpassword123",
    }

    # When: 사용자 등록 엔드포인트 호출
    response = await client.post("/api/v1/users/register", json=user_data)

    # Then: 등록 성공 검증
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "User registered successfully"

    # DB에 사용자 저장 검증
    result = await db_session.execute(
        select(User).where(User.username == "testuser"),
    )
    registered_user = result.scalar_one()

    assert registered_user is not None
    assert registered_user.username == "testuser"
    assert registered_user.verify_password("strongpassword123")


async def test_duplicate_username_registration(
    client: AsyncClient,
):
    """
    중복된 사용자명으로 등록 시도 테스트
    """
    # Given: 중복 사용자 정보
    user_data = {
        "username": "duplicateuser",
        "password": "strongpassword123",
    }

    # When: 첫 번째 등록
    first_response = await client.post("/api/v1/users/register", json=user_data)
    assert first_response.status_code == status.HTTP_200_OK

    # When: 동일한 사용자명으로 재등록
    second_response = await client.post("/api/v1/users/register", json=user_data)

    # Then: 중복 등록 오류 검증
    assert second_response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already registered" in second_response.json()["detail"]


async def test_registration_with_invalid_username(
    client: AsyncClient,
):
    """
    유효하지 않은 사용자명으로 등록 시도 테스트
    """
    # When: 너무 짧은 사용자명으로 등록
    user_data = {
        "username": "ab",  # 최소 길이 3 미만
        "password": "strongpassword123",
    }
    response = await client.post("/api/v1/users/register", json=user_data)

    # Then: 유효성 검사 실패 검증
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_registration_with_invalid_password(
    client: AsyncClient,
):
    """
    유효하지 않은 비밀번호로 등록 시도 테스트
    """
    # When: 너무 짧은 비밀번호로 등록
    user_data = {
        "username": "validuser",
        "password": "short",  # 최소 길이 8 미만
    }
    response = await client.post("/api/v1/users/register", json=user_data)

    # Then: 유효성 검사 실패 검증
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# 로그인 테스트 (이전에 작성한 로그인 관련 테스트 코드)
async def test_successful_user_login(
    client: AsyncClient,
    db_session: AsyncSession,
):
    """
    성공적인 사용자 로그인 테스트
    """
    # Given: 사전에 사용자 생성
    test_user = User(
        username="loginuser",
        password_hash=get_password_hash("strongpassword123"),
    )
    db_session.add(test_user)
    await db_session.commit()

    # When: 로그인 요청
    login_data = {
        "username": "loginuser",
        "password": "strongpassword123",
    }
    response = await client.post("/api/v1/users/login", json=login_data)

    # Then: 로그인 성공 검증
    assert response.status_code == status.HTTP_200_OK

    # 토큰 응답 검증
    response_data = response.json()
    assert "access_token" in response_data
    assert "refresh_token" in response_data
    assert response_data["token_type"] == "bearer"

    # 마지막 로그인 시간 검증
    result = await db_session.execute(
        select(User).where(User.username == "loginuser"),
    )
    updated_user = result.scalar_one()
    assert updated_user.last_login is not None


async def test_login_with_incorrect_password(
    client: AsyncClient,
    db_session: AsyncSession,
):
    """
    잘못된 비밀번호로 로그인 시도 테스트
    """
    # Given: 사전에 사용자 생성
    test_user = User(
        username="passwordtest",
        password_hash=get_password_hash("correctpassword"),
    )
    db_session.add(test_user)
    await db_session.commit()

    # When: 잘못된 비밀번호로 로그인 시도
    login_data = {
        "username": "passwordtest",
        "password": "wrongpassword",
    }
    response = await client.post("/api/v1/users/login", json=login_data)

    # Then: 인증 실패 검증
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]


async def test_login_with_nonexistent_user(
    client: AsyncClient,
):
    """
    존재하지 않는 사용자로 로그인 시도 테스트
    """
    # When: 존재하지 않는 사용자로 로그인 시도
    login_data = {
        "username": "nonexistentuser",
        "password": "somepassword",
    }
    response = await client.post("/api/v1/users/login", json=login_data)

    # Then: 인증 실패 검증
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]


async def test_login_with_invalid_username(
    client: AsyncClient,
):
    """
    유효하지 않은 사용자명으로 로그인 시도 테스트
    """
    # When: 너무 짧은 사용자명으로 로그인 시도
    login_data = {
        "username": "ab",  # 최소 길이 3 미만
        "password": "strongpassword123",
    }
    response = await client.post("/api/v1/users/login", json=login_data)

    # Then: 유효성 검사 실패 검증
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_login_with_invalid_password(
    client: AsyncClient,
):
    """
    유효하지 않은 비밀번호로 로그인 시도 테스트
    """
    # When: 너무 짧은 비밀번호로 로그인 시도
    login_data = {
        "username": "validuser",
        "password": "short",  # 최소 길이 8 미만
    }

    response = await client.post("/api/v1/users/login", json=login_data)

    # Then: 유효성 검사 실패 검증
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
