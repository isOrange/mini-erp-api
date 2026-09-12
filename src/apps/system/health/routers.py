from fastapi import APIRouter

from src.apps.system.health.services import get_health_status

# APIRouter 是一个“子路由容器”，用于把某个模块的接口集中管理。
# main.py 会通过 app.include_router(...) 把它注册到主应用。
router = APIRouter(tags=["System Health"])

@router.get("/health")
async def health():
    # router 层只负责接收 HTTP 请求，真正逻辑交给 service 层。
    return await get_health_status()