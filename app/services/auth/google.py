from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_or_create_user(db: AsyncSession, user_info: dict) -> tuple[User, bool]:
    """
    Google 사용자 정보를 바탕으로 DB에서 사용자를 조회하거나 생성합니다.
    새로운 사용자 생성 여부를 함께 반환합니다.

    Returns:
        Tuple[User, bool]: (사용자 객체, 새로운 사용자 여부)
    """
    user = await db.execute(
        select(User).where(User.email == user_info["email"]),
    )
    user = user.scalar_one_or_none()
    if not user:
        user = User(
            email=user_info["email"],
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user, True

    return user, False
