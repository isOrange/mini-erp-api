# 暴露http接口

from fastapi import APIRouter, HTTPException

from src.apps.system.users.schemas import UserRead, UserCreate
from src.apps.system.users.services import create_user, get_users, get_user

# prefix 会统一给当前 router 下的所有接口加路径前缀，例如 /users。
# tags 只影响 Swagger 文档分组，不影响接口路径和业务逻辑。
router = APIRouter(prefix="/users", tags=["System - Users"])

@router.post("", response_model=UserRead)
async def create_user_api(user: UserCreate):
    return await create_user(user)


@router.get("",response_model=list[UserRead])
async def get_users_api():
    return await get_users()


@router.get("/{user_id}",response_model=UserRead)
async def get_user_api(user_id: int):
    user = await get_user(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user