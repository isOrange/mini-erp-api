# 处理用户逻辑

from src.apps.system.users.schemas import UserRead, UserCreate, UserInDB

# 临时假数据库，程序重启后会清空
users_db: list[UserInDB] = []
# 模拟数据库自增 ID
next_user_id: int = 1


def fake_hashed_password(password: str) -> str:
    """学习用的假哈希：先理解密码不能明文保存。"""
    return "hashed_" + password


def to_user_read(user: UserInDB) -> UserRead:
    """把内部用户模型转换成接口返回模型，避免泄露 hashed_password。"""
    return UserRead(
        id=user.id,
        username=user.username,
        email=user.email,
    )


async def create_user(user: UserCreate) -> UserRead:
    global next_user_id

    new_user = UserInDB(
        id=next_user_id,
        username=user.username,
        email=user.email,
        hashed_password=fake_hashed_password(user.password),
    )
    users_db.append(new_user)
    next_user_id += 1
    return to_user_read(new_user)


async def get_users() -> list[UserRead]:
    return [to_user_read(user) for user in users_db]


async def get_user(user_id: int) -> UserRead | None:
    for user in users_db:
        if user.id == user_id:
            return to_user_read(user)

    return None

async def get_user_in_db_by_username(username: str) -> UserInDB | None:
    """根据 username 查询内部用户数据，供登录认证使用。"""

    for user in users_db:
        if user.username == username:
            return user

    return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码和内部保存的哈希密码是否匹配。"""
    return fake_hashed_password(plain_password) == hashed_password

