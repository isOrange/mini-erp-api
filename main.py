from fastapi import FastAPI
from src.apps.system.health.routers import router as health_router
from src.apps.system.users.routers import router as user_router
from src.apps.system.auth.routers import router as auth_router
from src.apps.business.products.routers import router as product_router

app = FastAPI(
    title="Mini ERP API",
    description="从零开始模仿FastAPI后端工程结构的学习项目",
    version="0.1.0"
)

app.include_router(health_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(product_router)


@app.get("/")
async def root():
    return {"message": "Mini ERP API is running2"}
