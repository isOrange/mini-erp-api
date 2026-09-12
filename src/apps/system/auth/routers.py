from fastapi import APIRouter, HTTPException, Header

from src.apps.system.auth.schemas import LoginRequest, Token
from src.apps.system.auth.services import login_user, get_current_user_by_token
from src.apps.system.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["System - Auth"])


@router.post("/login", response_model=Token)
async def login_api(login_data: LoginRequest):
    token = await login_user(login_data)
    if token is None:
        raise HTTPException(status_code=401, detail="Wrong username or password")

    return token


@router.get("/me", response_model=UserRead)
async def read_current_user(authorization: str | None = Header(default=None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = await get_current_user_by_token(authorization)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user
