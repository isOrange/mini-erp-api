async def get_health_status():
    # service 层负责业务逻辑；现在只是返回健康状态，后面可以扩展数据库/缓存检查。
    return {"status": "ok"}
