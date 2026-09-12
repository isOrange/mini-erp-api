from src.apps.business.products.schemas import ProductRead, ProductCreate, ProductUpdate

products_db: list[ProductRead] = [
    ProductRead(
        id=1,
        name="基础款白色T恤",
        sku="SKU-TSHIRT-001",
        price=99.0,
        stock=100,
        is_active=True,
    ),
    ProductRead(
        id=2,
        name="高腰牛仔裤",
        sku="SKU-JEANS-001",
        price=199.0,
        stock=50,
        is_active=True,
    ),
    ProductRead(
        id=3,
        name="下架测试商品",
        sku="SKU-OFF-001",
        price=59.0,
        stock=0,
        is_active=False,
    ),
]

next_product_id: int = 4


async def create_product(product: ProductCreate) -> ProductRead:
    """创建商品，并返回创建后的商品。"""

    global next_product_id

    new_product = ProductRead(
        id=next_product_id,
        name=product.name,
        sku=product.sku,
        price=product.price,
        stock=product.stock,
        is_active=True
    )

    products_db.append(new_product)
    next_product_id += 1

    return new_product


async def get_products() -> list[ProductRead]:
    """获取商品列表。"""

    return products_db


async def get_product(product_id: int) -> ProductRead | None:
    """根据商品 ID 查询单个商品。"""

    for product in products_db:
        if product.id == product_id:
            return product

    return None


async def update_product(product_id: int, product_update: ProductUpdate) -> ProductRead | None:
    """根据商品 ID 修改商品。"""

    product = await get_product(product_id)

    if product is None:
        return None

    update_data = product_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(product, key, value)

    return product


async def delete_product(product_id: int) -> bool:
    """根据商品 ID 删除商品。"""

    product = await get_product(product_id)

    if product is None:
        return False

    products_db.remove(product)

    return True
