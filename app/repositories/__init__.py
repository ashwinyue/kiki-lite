"""仓储层模块

提供数据库操作的抽象层。
"""

from sqlalchemy import desc, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Session, Message


class BaseRepository:
    """基础仓储类"""

    def __init__(self, model, session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get(self, id: str):
        statement = select(self.model).where(self.model.id == id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, obj):
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: str) -> bool:
        obj = await self.get(id)
        if obj:
            await self.session.delete(obj)
            return True
        return False

    async def count(self, **filters) -> int:
        statement = select(func.count()).select_from(self.model)
        for field, value in filters.items():
            statement = statement.where(getattr(self.model, field) == value)
        result = await self.session.execute(statement)
        return result.scalar() or 0


class SessionRepository(BaseRepository):
    """会话仓储"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Session, session)

    async def list_by_user(self, user_id: str | None = None, limit: int = 100):
        statement = select(Session)
        if user_id:
            statement = statement.where(Session.user_id == user_id)
        statement = statement.order_by(desc(Session.created_at)).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())


class MessageRepository(BaseRepository):
    """消息仓储"""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Message, session)

    async def list_by_session(self, session_id: str, limit: int = 100):
        statement = select(Message)
        statement = statement.where(Message.session_id == session_id)
        statement = statement.order_by(Message.created_at.asc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())


__all__ = [
    "BaseRepository",
    "SessionRepository",
    "MessageRepository",
]
