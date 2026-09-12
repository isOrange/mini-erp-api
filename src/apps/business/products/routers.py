from fastapi import APIRouter, HTTPException

from src.apps.business.products.schemas import ProductRead, ProductCreate, ProductUpdate

from src.apps.business.products.services import (
    create_product,
    get_products, get_product,
    update_product,
    delete_product
)

router = APIRouter(prefix="/products", tags=["Business - Products"])


@router.post("", response_model=ProductRead)
async def create_product_api(product: ProductCreate):
    """创建商品接口。"""
    return await create_product(product)


@router.get("", response_model=list[ProductRead])
async def get_products_api():
    """查询商品列表接口。"""
    return await get_products()


@router.get("/{product_id}", response_model=ProductRead)
async def get_product_api(product_id: int):
    """查询单个商品接口。"""

    product = await get_product(product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product_api(product_id: int, product_update: ProductUpdate):
    """修改商品接口。"""

    product = await update_product(product_id, product_update)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.delete("/{product_id}")
async def delete_product_api(product_id: int):
    """删除商品接口。"""

    success = await delete_product(product_id)

    if not success:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}
