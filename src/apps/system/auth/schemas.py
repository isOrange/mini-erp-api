from pydantic import BaseModel


class LoginRequest(BaseModel):
    """登录时客户端提交的数据。"""

    username: str
    password: str

class Token(BaseModel):
    """登录成功后返回给客户端的令牌数据。"""

    access_token: str
    token_type: str