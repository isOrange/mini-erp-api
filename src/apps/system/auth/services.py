from datetime import datetime, timedelta, timezone

import jwt

from src.apps.system.auth.schemas import LoginRequest, Token
from src.apps.system.users.schemas import UserRead
from src.apps.system.users.services import (
    get_user_in_db_by_username,
    verify_password
)

# 学习阶段先写死密钥；真实项目要放到 .env，不能提交到 GitHub。
# SECRET_KEY：服务器用来签名和验签的密钥
# ALGORITHM：签名算法
# ACCESS_TOKEN_EXPIRE_MINUTES：access token 有效期
SECRET_KEY = "dev-secret-key-change-me-please-32-bytes"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(username: str) -> str:
    """创建 access token。"""

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": username,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def parse_access_token(token: str) -> str | None:
    """解析 access token，成功时返回 username。"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None

    username = payload.get("sub")
    if username is None:
        return None

    return username


async def get_current_user_by_token(token: str) -> UserRead | None:
    """根据 access token 获取当前用户。"""

    bearer_prefix = "Bearer "
    if token.startswith(bearer_prefix):
        token = token.removeprefix(bearer_prefix)

    username = parse_access_token(token)
    if username is None:
        return None

    user = await get_user_in_db_by_username(username=username)
    if user is None:
        return None

    return UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
    )


async def login_user(login_data: LoginRequest) -> Token | None:
    """校验用户名和密码，成功时返回 access token。"""

    user = await get_user_in_db_by_username(login_data.username)

    if user is None:
        return None

    if not verify_password(login_data.password, user.hashed_password):
        return None

    return Token(
        access_token=create_access_token(login_data.username),
        token_type="bearer",
    )
