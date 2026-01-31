"""应用入口（简化版）

创建 FastAPI 应用并配置核心组件。
"""

from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 加载 .env 文件
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    yield


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="Kiki Lite",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    from app.api.v1 import router as api_v1_router
    from app.config.settings import get_settings

    settings = get_settings()
    app.include_router(api_v1_router, prefix=settings.api_prefix)

    @app.get("/health")
    async def health():
        return {"status": "healthy", "version": "0.1.0"}

    @app.get("/")
    async def root():
        return {"name": "Kiki Lite", "version": "0.1.0"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
