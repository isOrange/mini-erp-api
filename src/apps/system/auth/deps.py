from fastapi import HTTPException, Header
from starlette import status

from src.apps.system.auth.services import get_current_user_by_token
from src.apps.system.users.schemas import UserRead


async def get_current_user(authorization: str | None = Header(default=None)) -> UserRead:
    """获取当前登录用户。"""
    if authorization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authenticated")

    user = await get_current_user_by_token(authorization)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid Token")

    return user
