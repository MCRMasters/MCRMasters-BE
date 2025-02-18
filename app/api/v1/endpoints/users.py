from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.session import get_session
from app.models.user import User
from app.schemas.base_response import BaseResponse
from app.schemas.user.user_create import UserCreate

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
            status_code=400,
            detail="Username already registered",
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
