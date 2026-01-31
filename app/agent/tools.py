"""工具系统

提供 LangChain 工具的注册、管理和执行。
"""

from collections.abc import Callable
from threading import RLock
from typing import Any

from langchain_core.tools import BaseTool, tool as lc_tool

from app.observability.logging import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    """工具注册表

    管理所有已注册的 LangChain 工具。
    线程安全实现。
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}
        self._lock = RLock()

    def register(self, tool_obj: BaseTool) -> None:
        """注册工具"""
        with self._lock:
            self._tools[tool_obj.name] = tool_obj
            logger.info("tool_registered", tool_name=tool_obj.name)

    def get(self, name: str) -> BaseTool | None:
        """获取工具"""
        with self._lock:
            return self._tools.get(name)

    def list_all(self) -> list[BaseTool]:
        """列出所有工具"""
        with self._lock:
            return list(self._tools.values())

    def clear(self) -> None:
        """清空注册表"""
        with self._lock:
            self._tools.clear()


# 全局注册表
_registry = ToolRegistry()


def register_tool(tool_obj: BaseTool) -> None:
    """注册工具到全局注册表"""
    _registry.register(tool_obj)


def get_tool(name: str) -> BaseTool | None:
    """获取工具"""
    return _registry.get(name)


def list_tools() -> list[BaseTool]:
    """列出所有工具"""
    return _registry.list_all()


def tool(*args: Any, **kwargs: Any) -> Callable:
    """工具装饰器

    Examples:
        from app.agent.tools import tool

        @tool
        def search_web(query: str) -> str:
            return f"Search result: {query}"
    """
    def decorator(func: Callable) -> BaseTool:
        tool_obj = lc_tool(*args, **kwargs)(func)
        register_tool(tool_obj)
        return tool_obj

    if args and callable(args[0]):
        func = args[0]
        return lc_tool(func)
    return decorator


# ============== 内置工具 ==============


@tool
def calculate(expression: str) -> str:
    """Calculate math expression

    Args:
        expression: Math expression like "2 + 3 * 4"

    Returns:
        Calculation result
    """
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


@tool
def get_weather(city: str) -> str:
    """Get weather (mock)

    Args:
        city: City name

    Returns:
        Weather info
    """
    return f"Weather in {city}: Sunny, 22C"


@tool
def search_web(query: str) -> str:
    """Web search (mock)

    Args:
        query: Search query

    Returns:
        Search result summary
    """
    return f"Search results for '{query}': This is a mock search result."


# 自动注册内置工具
for tool_obj in [search_web, calculate, get_weather]:
    register_tool(tool_obj)


__all__ = [
    "ToolRegistry",
    "register_tool",
    "get_tool",
    "list_tools",
    "tool",
]
