from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_health_status():
    """返回应用自身健康状态。"""
    return {"status": "ok"}


async def get_ready_status(db: AsyncSession):
    """
    检查应用依赖是否已经可用。

    Args:
        db: 当前请求使用的数据库会话。

    Returns:
        服务依赖检查结果。
    """
    await db.execute(text("SELECT 1"))
    return {
        "status": "ready",
        "database": "ok",
    }