from pydantic import BaseModel


class ProductCreate(BaseModel):
    """商品创建入参：客户端创建商品时提交的数据。"""

    name: str
    sku: str
    price: float
    stock: int


class ProductUpdate(BaseModel):
    """商品修改入参：客户端可以只提交需要修改的字段。"""
    name: str | None = None
    sku: str | None = None
    price: float | None = None
    stock: int | None = None
    is_active: bool | None = None


class ProductRead(BaseModel):
    """商品返回模型：接口返回给前端看的商品数据。"""
    id: int
    name: str
    sku: str
    price: float
    stock: int
    is_active: bool
