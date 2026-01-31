"""记忆管理

提供对话记忆的存储和管理。
"""

from datetime import datetime
from typing import Any

from app.observability.logging import get_logger

logger = get_logger(__name__)


class MemoryManager:
    """记忆管理器

    管理对话历史和记忆。
    """

    def __init__(self, max_messages: int = 20) -> None:
        """初始化记忆管理器

        Args:
            max_messages: 最大保留消息数量
        """
        self._sessions: dict[str, list[dict[str, Any]]] = {}
        self._max_messages = max_messages

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        **extra: Any,
    ) -> None:
        """添加消息

        Args:
            session_id: 会话 ID
            role: 角色 (user/assistant/system)
            content: 消息内容
            **extra: 额外字段
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            **extra,
        }

        self._sessions[session_id].append(message)

        # 限制消息数量
        if len(self._sessions[session_id]) > self._max_messages:
            self._sessions[session_id] = self._sessions[session_id][-self._max_messages:]

        logger.debug("message_added", session_id=session_id, role=role)

    async def get_messages(
        self,
        session_id: str,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """获取消息历史

        Args:
            session_id: 会话 ID
            limit: 最大消息数量

        Returns:
            消息列表
        """
        messages = self._sessions.get(session_id, [])
        if limit:
            messages = messages[-limit:]
        return messages

    async def clear_session(self, session_id: str) -> None:
        """清除会话

        Args:
            session_id: 会话 ID
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info("session_cleared", session_id=session_id)

    async def list_sessions(self) -> list[str]:
        """列出所有会话 ID

        Returns:
            会话 ID 列表
        """
        return list(self._sessions.keys())


# 全局记忆管理器
_memory_manager: MemoryManager | None = None


def get_memory_manager() -> MemoryManager:
    """获取全局记忆管理器"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


__all__ = [
    "MemoryManager",
    "get_memory_manager",
]
