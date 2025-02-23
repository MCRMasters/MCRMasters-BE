from random import randint

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.util.validators import validate_uid


async def generate_unique_uid(db: AsyncSession) -> str:
    while True:
        uid = str(randint(100000000, 999999999))

        try:
            validate_uid(uid)
            result = await db.execute(
                select(User).where(User.uid == uid),
            )
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                return uid

        except Exception:
            continue


async def get_or_create_user(db: AsyncSession, user_info: dict) -> tuple[User, bool]:
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
        return user, True

    return user, user.nickname == ""
