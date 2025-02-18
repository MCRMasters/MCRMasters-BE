from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

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
    print(response.json())
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
