from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.system.health.services import get_health_status, get_ready_status
from src.core.database import get_db_session

router = APIRouter(tags=["System Health"])


@router.get("/health")
async def health():
    """检查应用进程是否存活。"""
    return await get_health_status()


@router.get("/ready")
async def ready(db: AsyncSession = Depends(get_db_session)):
    """检查应用依赖是否可用。"""
    return await get_ready_status(db)