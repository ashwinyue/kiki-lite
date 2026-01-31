"""消息管理 API"""

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.config.settings import get_settings

router = APIRouter(prefix="/messages", tags=["messages"])

# 内存存储（简化）
_messages: list[dict] = []


class MessageCreateRequest(BaseModel):
    session_id: str
    role: str
    content: str


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: str


@router.get("/session/{session_id}")
async def list_messages(session_id: str, limit: int = 100) -> list[MessageResponse]:
    """获取会话的消息历史"""
    msgs = [m for m in _messages if m["session_id"] == session_id][-limit:]
    return [MessageResponse(**m) for m in msgs]


@router.post("", response_model=MessageResponse)
async def create_message(request: MessageCreateRequest) -> MessageResponse:
    """创建消息"""
    from datetime import datetime

    msg = {
        "id": str(uuid4()),
        "session_id": request.session_id,
        "role": request.role,
        "content": request.content,
        "created_at": datetime.now().isoformat(),
    }
    _messages.append(msg)
    return MessageResponse(**msg)


@router.delete("/{message_id}")
async def delete_message(message_id: str) -> dict:
    """删除消息"""
    global _messages
    if not any(m["id"] == message_id for m in _messages):
        raise HTTPException(status_code=404, detail="消息不存在")
    _messages = [m for m in _messages if m["id"] != message_id]
    return {"message": "删除成功"}


__all__ = ["router"]
