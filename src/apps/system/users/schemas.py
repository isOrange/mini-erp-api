# 定义数据长什么样

from pydantic import BaseModel



class UserCreate(BaseModel):
    """创建用户时，客户端提交的数据。"""
    username: str
    password: str
    email: str


class UserRead(BaseModel):
    """接口返回给客户端的用户数据，不能包含密码。"""
    id: int
    username: str
    email: str


class UserInDB(BaseModel):
    """服务端内部保存的用户数据，包含哈希后的密码。"""
    id: int
    username: str
    email: str
    hashed_password: str
