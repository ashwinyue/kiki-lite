"""会话管理 API"""

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config.settings import get_settings
from app.models import Session

router = APIRouter(prefix="/sessions", tags=["sessions"])

# 内存存储（简化）
_sessions: dict[str, dict] = {}


class SessionCreateRequest(BaseModel):
    title: str | None = None


class SessionResponse(BaseModel):
    id: str
    title: str | None
    created_at: str


@router.get("")
async def list_sessions() -> list[SessionResponse]:
    """列出所有会话"""
    return [
        SessionResponse(id=sid, **data)
        for sid, data in _sessions.items()
    ]


@router.post("", response_model=SessionResponse)
async def create_session(request: SessionCreateRequest) -> SessionResponse:
    """创建新会话"""
    from datetime import datetime

    sid = str(uuid4())
    session = {
        "title": request.title or "新对话",
        "created_at": datetime.now().isoformat(),
    }
    _sessions[sid] = session

    return SessionResponse(id=sid, **session)


@router.get("/{session_id}")
async def get_session(session_id: str) -> SessionResponse:
    """获取会话详情"""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    return SessionResponse(id=session_id, **_sessions[session_id])


@router.delete("/{session_id}")
async def delete_session(session_id: str) -> dict:
    """删除会话"""
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    del _sessions[session_id]
    return {"message": "删除成功"}


__all__ = ["router"]
