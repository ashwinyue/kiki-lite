"""依赖注入模块

提供 FastAPI 依赖注入提供者。
"""

from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config.settings import Settings, get_settings


# ============== 数据库 ==============

@lru_cache
def _get_engine():
    """获取数据库引擎（缓存）"""
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=settings.database_pool_size,
    )


_async_session_factory = None


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    """获取会话工厂"""
    global _async_session_factory
    if _async_session_factory is None:
        engine = _get_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _async_session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """数据库会话依赖注入"""
    factory = _get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ============== LLM Service ==============


def get_llm_service() -> "LLMService":
    """获取 LLM 服务"""
    from app.llm import get_llm_service as _get

    return _get()


# ============== 当前用户 ==============


async def get_current_user(
    authorization: str | None = None,
) -> dict | None:
    """获取当前用户（简化实现）

    从 Authorization header 解析用户信息。
    生产环境应使用完整的 JWT 验证。
    """
    if not authorization:
        return None

    # 简化实现：直接从 header 解析
    # 生产环境应验证 JWT token
    try:
        import base64
        # 这里应该是 JWT 验证逻辑
        # 简化示例：假设 token 是 base64 编码的 user_id
        return {"id": "user-123", "name": "Test User"}
    except Exception:
        return None


__all__ = [
    "get_session",
    "get_llm_service",
    "get_current_user",
]
