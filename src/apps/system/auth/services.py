from src.apps.system.auth.schemas import LoginRequest, Token
from src.apps.system.users.schemas import UserRead
from src.apps.system.users.services import (
    get_user_in_db_by_username,
    verify_password
)


def create_fake_access_token(username: str):
    """学习用的假 token：先理解登录成功后返回 access_token。"""

    return "fake-token-for-" + username


def parse_fake_access_token(token: str) -> str | None:
    """解析学习用 fake token，成功时返回 username。"""

    prefix = "fake-token-for-"
    if not token.startswith(prefix):
        return None

    return token.removeprefix(prefix)


async def get_current_user_by_token(token: str) -> UserRead | None:
    """根据 access token 获取当前用户。"""

    bearer_prefix = "Bearer "
    if token.startswith(bearer_prefix):
        token = token.removeprefix(bearer_prefix)

    username = parse_fake_access_token(token)
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
        access_token=create_fake_access_token(login_data.username),
        token_type="bearer",
    )
