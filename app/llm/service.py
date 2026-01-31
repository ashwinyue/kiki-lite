"""LLM 服务

提供 LLM 模型管理，支持 DashScope 和 OpenAI。
"""

from enum import Enum
from typing import Any

from langchain_openai import ChatOpenAI

from app.config.settings import get_settings
from app.observability.logging import get_logger

logger = get_logger(__name__)


class LLMProvider(str, Enum):
    """LLM 提供商"""
    OPENAI = "openai"
    DASHSCOPE = "dashscope"


class LLMService:
    """LLM 服务"""

    def __init__(self) -> None:
        """初始化 LLM 服务"""
        self._models: dict[str, Any] = {}
        self._settings = get_settings()

    def get_model(self, provider: LLMProvider | None = None, model_name: str | None = None) -> Any:
        """获取模型"""
        provider = provider or LLMProvider(self._settings.llm_provider)
        model_name = model_name or self._settings.llm_model

        key = f"{provider}:{model_name}"
        if key in self._models:
            return self._models[key]

        model = self._create_model(provider, model_name)
        self._models[key] = model
        return model

    def _create_model(self, provider: LLMProvider, model_name: str) -> Any:
        """创建模型实例"""
        if provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                model=model_name,
                api_key=self._settings.openai_api_key,
                temperature=0.7,
            )
        elif provider == LLMProvider.DASHSCOPE:
            return ChatOpenAI(
                model=model_name,
                api_key=self._settings.dashscope_api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=0.7,
            )
        else:
            raise ValueError(f"不支持的 LLM 提供商: {provider}")


_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """获取全局 LLM 服务"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


__all__ = [
    "LLMProvider",
    "LLMService",
    "get_llm_service",
]
