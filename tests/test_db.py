from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def test_db_connection(db_session: AsyncSession):
    result = await db_session.execute(text("SELECT 1"))
    value = result.scalar()

    assert value == 1
