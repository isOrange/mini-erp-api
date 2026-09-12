from src.apps.system.auth.schemas import LoginRequest, Token
from src.apps.system.users.schemas import UserRead
from src.apps.system.users.services import (
    get_user_in_db_by_username,
    verify_password, to_user_read
)


def create_fake_access_token(username: str):
    """学习用的假 token：先理解登录成功后返回 access_token。"""

    return "fake_token_for" + username


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
