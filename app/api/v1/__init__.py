"""API v1 路由"""

from fastapi import APIRouter

from app.api.v1 import chat, sessions, messages

router = APIRouter()

router.include_router(chat.router)
router.include_router(sessions.router)
router.include_router(messages.router)

__all__ = ["router"]
