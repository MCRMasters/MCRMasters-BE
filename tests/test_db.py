import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_db_connection(db_session: AsyncSession):
    result = await db_session.execute(text("SELECT 1"))
    value = result.scalar()

    assert value == 1, "데이터베이스 연결 테스트 실패"
