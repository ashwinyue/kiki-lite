"""聊天 API"""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent.agent import AgentManager
from app.agent.tools import list_tools
from app.config.settings import get_settings

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: str
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("")
async def chat(
    request: ChatRequest,
    llm_service: "LLMService" = Depends(lambda: get_llm_service()),
) -> ChatResponse:
    """发送消息并获取响应（同步）"""
    from app.llm import get_llm_service

    llm_service = get_llm_service()
    model = llm_service.get_model()
    tools = list_tools()
    agent = AgentManager(model=model, tools=tools)

    response = await agent.chat_sync(
        message=request.message,
        session_id=request.session_id,
    )

    return ChatResponse(response=response, session_id=request.session_id)


@router.post("/stream")
async def stream_chat(request: ChatRequest):
    """发送消息并获取响应（流式）"""
    from app.llm import get_llm_service

    llm_service = get_llm_service()
    model = llm_service.get_model()
    tools = list_tools()
    agent = AgentManager(model=model, tools=tools)

    async def generate():
        async for chunk in agent.chat(
            message=request.message,
            session_id=request.session_id,
        ):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str) -> dict:
    """获取聊天历史"""
    from app.agent.memory import get_memory_manager

    manager = get_memory_manager()
    messages = await manager.get_messages(session_id)

    return {"messages": messages, "session_id": session_id}


# 延迟导入避免循环依赖
def get_llm_service():
    from app.llm import get_llm_service as _get
    return _get()


__all__ = ["router"]
