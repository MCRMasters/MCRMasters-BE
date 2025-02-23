import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from app.core.config import get_test_settings


@pytest_asyncio.fixture
async def test_engine():
    """테스트 DB 엔진 설정"""
    test_settings = get_test_settings()
    engine = create_async_engine(
        test_settings.database_uri,
        echo=False,
        future=True,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_engine) -> AsyncSession:
    """테스트용 DB 세션"""
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


# 실제 DB 연결 테스트
async def test_db_connection(test_db_session: AsyncSession):
    """데이터베이스 연결 테스트"""
    result = await test_db_session.execute(text("SELECT 1"))
    value = result.scalar()

    assert value == 1


# 트랜잭션 롤백 테스트
async def test_transaction_rollback(test_db_session: AsyncSession):
    """트랜잭션 롤백 테스트"""
    # 테스트 데이터 생성
    await test_db_session.execute(
        text("CREATE TABLE IF NOT EXISTS test_table (id INT)"),
    )
    await test_db_session.execute(text("INSERT INTO test_table (id) VALUES (1)"))
    await test_db_session.commit()

    # 데이터 확인
    result = await test_db_session.execute(text("SELECT COUNT(*) FROM test_table"))
    assert result.scalar() == 1

    # 롤백 테스트
    await test_db_session.execute(text("INSERT INTO test_table (id) VALUES (2)"))
    await test_db_session.rollback()

    # 롤백 후 데이터 확인
    result = await test_db_session.execute(text("SELECT COUNT(*) FROM test_table"))
    assert result.scalar() == 1

    # 테스트 테이블 정리
    await test_db_session.execute(text("DROP TABLE test_table"))
    await test_db_session.commit()
