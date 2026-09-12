from fastapi import APIRouter, HTTPException

from src.apps.system.auth.schemas import LoginRequest, Token
from src.apps.system.auth.services import login_user
from src.apps.system.users.schemas import UserRead

router = APIRouter(prefix="/auth", tags=["System - Auth"])


@router.post("/login", response_model=Token)
async def login_api(login_data: LoginRequest):
    token = await login_user(login_data)
    if token is None:
        raise HTTPException(status_code=401, detail="Wrong username or password")

    return token
