"""LangGraph Agent

基于 LangGraph 原生能力实现 Agent，支持工具调用和对话状态管理。
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Annotated, Any

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import create_react_agent, ToolNode
from langgraph.checkpoint.memory import MemorySaver

from app.observability.logging import get_logger

logger = get_logger(__name__)


@dataclass
class AgentState:
    """Agent 状态

    Attributes:
        messages: 对话消息历史
        user_id: 用户 ID
        session_id: 会话 ID
        iteration_count: 迭代次数（防止无限循环）
    """
    messages: list[BaseMessage] = field(default_factory=list)
    user_id: str | None = None
    session_id: str | None = None
    iteration_count: int = 0


def create_agent(
    model: Any,
    tools: list[BaseTool],
    max_iterations: int = 10,
) -> Any:
    """创建 Agent

    使用 create_react_agent 快速创建支持工具调用的 Agent。

    Args:
        model: LangChain LLM 模型
        tools: 工具列表
        max_iterations: 最大迭代次数

    Returns:
        编译后的 Agent
    """
    # 使用内存检查点（生产环境可替换为 PostgreSQL）
    checkpointer = MemorySaver()

    # 创建 ReAct Agent
    agent = create_react_agent(
        model=model,
        tools=tools,
        checkpointer=checkpointer,
        debug=False,
    )

    return agent


def create_agent_graph(
    model: Any,
    tools: list[BaseTool],
) -> StateGraph:
    """创建自定义 Agent 图（高级用法）

    如果需要更细粒度的控制，可以使用 StateGraph 自定义图结构。

    Args:
        model: LangChain LLM 模型
        tools: 工具列表

    Returns:
        StateGraph 实例
    """
    def should_continue(state: AgentState) -> str:
        """判断是否继续执行工具调用"""
        last_message = state.messages[-1] if state.messages else None
        if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    def call_model(state: AgentState) -> dict[str, Any]:
        """调用 LLM 生成回复"""
        response = model.invoke(state.messages)
        return {"messages": [response]}

    def call_tools(state: AgentState) -> dict[str, Any]:
        """执行工具调用"""
        tool_node = ToolNode(tools)
        return tool_node.invoke(state)

    # 构建图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", call_tools)

    # 添加边
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", should_continue)
    workflow.add_conditional_edges("tools", should_continue)

    return workflow


class AgentManager:
    """Agent 管理器

    管理 Agent 实例和对话状态。
    """

    def __init__(
        self,
        model: Any,
        tools: list[BaseTool],
        checkpointer: Any = None,
    ) -> None:
        """初始化 Agent 管理器

        Args:
            model: LLM 模型
            tools: 工具列表
            checkpointer: 状态检查点保存器
        """
        self._model = model
        self._tools = tools
        self._agent = create_agent(model, tools)
        self._checkpointer = checkpointer

    async def chat(
        self,
        message: str,
        session_id: str,
        user_id: str | None = None,
    ) -> AsyncIterator[str]:
        """流式对话

        Args:
            message: 用户消息
            session_id: 会话 ID
            user_id: 用户 ID

        Yields:
            响应文本片段
        """
        from langchain_core.messages import HumanMessage

        config = {"configurable": {"thread_id": session_id}}

        # 流式获取响应
        async for chunk in self._agent.astream(
            {"messages": [HumanMessage(content=message)]},
            config=config,
            stream_mode="messages",
        ):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content

    async def chat_sync(
        self,
        message: str,
        session_id: str,
        user_id: str | None = None,
    ) -> str:
        """同步对话

        Args:
            message: 用户消息
            session_id: 会话 ID
            user_id: 用户 ID

        Returns:
            完整响应文本
        """
        from langchain_core.messages import HumanMessage

        config = {"configurable": {"thread_id": session_id}}

        result = await self._agent.ainvoke(
            {"messages": [HumanMessage(content=message)]},
            config=config,
        )

        # 提取最后一条 AI 消息
        for msg in reversed(result["messages"]):
            if isinstance(msg, AIMessage):
                return str(msg.content)
        return ""


__all__ = [
    "AgentState",
    "AgentManager",
    "create_agent",
    "create_agent_graph",
]
