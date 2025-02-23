from random import randint

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.util.validators import validate_uid


async def generate_unique_uid(db: AsyncSession) -> str:
    """
    유니크한 9자리 UID를 생성합니다.
    100000000부터 999999999까지의 범위에서 생성합니다.

    Args:
        db: 데이터베이스 세션

    Returns:
        str: 유니크한 9자리 UID
    """
    while True:
        # 100000000 ~ 999999999 범위의 난수 생성
        uid = str(randint(100000000, 999999999))

        try:
            # UID 형식 검증
            validate_uid(uid)

            # DB에서 중복 체크
            result = await db.execute(
                select(User).where(User.uid == uid),
            )
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                return uid

        except Exception:
            continue


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
        new_uid = await generate_unique_uid(db)
        user = User(
            email=user_info["email"],
            uid=new_uid,
            nickname="",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user, True

    return user, user.nickname == ""
