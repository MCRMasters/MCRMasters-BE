from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
)
from app.db.session import get_session
from app.models.user import User
from app.schemas.base_response import BaseResponse
from app.schemas.user.user_create import UserCreate
from app.schemas.user.user_login import TokenResponse, UserLogin

router = APIRouter()


@router.post("/register", response_model=BaseResponse)
async def register_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_session),
):
    try:
        # 새로운 유저 객체 생성
        user = User(
            username=user_create.username,
            password_hash=get_password_hash(user_create.password),
        )

        # DB에 저장
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return BaseResponse(
            message="User registered successfully",
        )

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_session),
):
    # 유저 조회 쿼리
    query = select(User).where(User.username == user_login.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # 사용자 인증 로직
    if not user or not user.verify_password(user_login.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 토큰 생성
    access_token = create_access_token(
        data={"sub": user.username},
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username},
    )

    # 마지막 로그인 시간 업데이트
    user.last_login = datetime.now(UTC)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
