"""数据模型定义（SQLModel）"""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class SessionBase(SQLModel):
    """会话基础模型"""
    title: str | None = Field(default=None, max_length=255)


class Session(SessionBase, table=True):
    """会话表模型"""
    __tablename__ = "sessions"

    id: str = Field(default=None, primary_key=True, max_length=36)
    user_id: str | None = Field(default=None, max_length=36)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MessageBase(SQLModel):
    """消息基础模型"""
    role: str = Field(max_length=50)
    content: str


class Message(MessageBase, table=True):
    """消息表模型"""
    __tablename__ = "messages"

    id: str = Field(default=None, primary_key=True, max_length=36)
    session_id: str = Field(max_length=36, foreign_key="sessions.id")
    user_id: str | None = Field(default=None, max_length=36)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


__all__ = [
    "Session",
    "Message",
]
