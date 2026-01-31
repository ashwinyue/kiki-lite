"""应用入口

创建 FastAPI 应用并配置所有组件。
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware

# 加载 .env 文件（必须在导入 app 模块之前执行）
load_dotenv()
from fastapi.responses import JSONResponse
from starlette.requests import Request as StarletteRequest

from app.config.errors import classify_error, get_user_friendly_message
from app.config.settings import get_settings
from app.middleware import (
    MaxRequestSizeMiddleware,
    ObservabilityMiddleware,
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
    TenantMiddleware,
)
from app.observability.logging import configure_logging, get_logger

# 获取配置
settings = get_settings()

# 配置日志
configure_logging(
    environment=settings.environment.value,
    log_level=settings.log_level,
    log_format=settings.log_format,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期管理"""
    logger.info(
        "app_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment.value,
    )

    yield

    # 关闭时清理
    logger.info("app_shutting_down")

    # 关闭 Redis 连接池
    from app.infra.redis import close_redis

    await close_redis()


def create_app() -> FastAPI:
    """创建 FastAPI 应用

    Returns:
        FastAPI 应用实例
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # ========== 添加中间件 ==========

    # 安全响应头 - 必须在最前面，确保所有响应都有安全头
    app.add_middleware(SecurityHeadersMiddleware)

    # 请求大小限制 - 在其他中间件之前检查
    app.add_middleware(MaxRequestSizeMiddleware, max_size=settings.max_request_size)

    # 可观测性中间件
    app.add_middleware(ObservabilityMiddleware)
    app.add_middleware(RequestContextMiddleware)

    # 租户认证中间件
    app.add_middleware(
        TenantMiddleware,
        enable_cross_tenant=settings.enable_cross_tenant,
    )

    # CORS 配置 - 允许前端跨域访问
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # TrustedHost - 防止 Host Header 攻击
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )

    # GZip 压缩 - 仅生产环境
    if not settings.is_development:
        app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 注册路由
    _register_routes(app)

    # 注册异常处理器
    _register_exception_handlers(app)

    return app


def _register_routes(app: FastAPI) -> None:
    """注册路由"""

    @app.get("/health")
    async def health_check():
        """健康检查

        检查应用状态和依赖服务（Redis）的健康状态。
        """
        from app.infra.redis import ping as redis_ping

        checks = {
            "app": "healthy",
            "version": settings.app_version,
        }

        # 检查 Redis 连接
        redis_status = await redis_ping()
        checks["redis"] = "healthy" if redis_status else "unhealthy"

        # 如果有依赖服务不健康，整体状态为 degraded
        if not redis_status:
            checks["status"] = "degraded"
        else:
            checks["status"] = "healthy"

        return checks

    @app.get("/")
    async def root():
        """根路径"""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment.value,
        }

    @app.get("/metrics")
    async def metrics():
        """Prometheus 指标"""
        from fastapi.responses import Response

        from app.observability.metrics import get_metrics_text

        return Response(
            content=get_metrics_text(),
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    # 注册 API 路由
    from app.api.v1 import router as api_v1_router

    app.include_router(api_v1_router, prefix=settings.api_prefix)


def _register_exception_handlers(app: FastAPI) -> None:
    """注册异常处理器"""

    @app.exception_handler(Exception)
    async def global_exception_handler(request: StarletteRequest, exc: Exception):
        """全局异常处理

        根据环境返回适当的错误信息：
        - 生产环境：不暴露敏感错误信息
        - 开发环境：显示详细错误
        """
        # 分类错误
        error_context = classify_error(exc)

        logger.exception(
            "unhandled_exception",
            path=request.url.path,
            error=str(exc),
            error_type=type(exc).__name__,
            error_category=error_context.category.value,
            error_severity=error_context.severity.value,
        )

        # 获取用户友好的错误消息
        user_message = get_user_friendly_message(exc, error_context)

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": user_message,
                "category": error_context.category.value if settings.debug else None,
            },
        )


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
    )
