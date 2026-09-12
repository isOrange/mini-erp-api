from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings


engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=1800,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    为每个请求提供独立的数据库会话。

    Yields:
        AsyncSession: 当前请求使用的数据库会话。
    """
    async with AsyncSessionLocal() as session:
        yield session