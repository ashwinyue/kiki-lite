"""数据模型定义（SQLModel）

对齐 WeKnora99 表结构
"""

# ============== 用户认证 ==============
from app.models.auth_token import (
    AuthToken,
    AuthTokenCreate,
    AuthTokenPublic,
)

# ============== Agent ==============
from app.models.custom_agent import (
    Agent,
    AgentCreate,
    AgentPublic,
    AgentUpdate,
    CustomAgent,
    CustomAgentCreate,
    CustomAgentPublic,
    CustomAgentUpdate,
)

# ============== MCP 服务 ==============
from app.models.mcp_service import (
    MCPService,
    MCPServiceCreate,
    MCPServicePublic,
    MCPServiceUpdate,
)

# ============== 会话 ==============
from app.models.memory import (
    Memory,
    MemoryCreate,
    MemoryPublic,
    MemoryUpdate,
)

# ============== 消息 ==============
from app.models.message import (
    Message,
    MessageCreate,
    MessagePublic,
    MessageUpdate,
)
from app.models.session import (
    ChatSession,
    Session,
    SessionCreate,
    SessionPublic,
    SessionUpdate,
)

# ============== 租户 ==============
from app.models.tenant import (
    Tenant,
    TenantCreate,
    TenantPublic,
    TenantUpdate,
)
from app.models.thread import (
    Thread,
    ThreadCreate,
    ThreadPublic,
)
from app.models.user import (
    User,
    UserCreate,
    UserPublic,
    UserUpdate,
    hash_password,
    verify_password,
)

__all__ = [
    # 用户认证
    "User",
    "UserCreate",
    "UserUpdate",
    "UserPublic",
    "hash_password",
    "verify_password",
    "AuthToken",
    "AuthTokenCreate",
    "AuthTokenPublic",
    # 租户
    "Tenant",
    "TenantCreate",
    "TenantUpdate",
    "TenantPublic",
    # 会话
    "Session",
    "ChatSession",
    "SessionCreate",
    "SessionUpdate",
    "SessionPublic",
    # 线程
    "Thread",
    "ThreadCreate",
    "ThreadPublic",
    # 长期记忆
    "Memory",
    "MemoryCreate",
    "MemoryUpdate",
    "MemoryPublic",
    # 消息
    "Message",
    "MessageCreate",
    "MessageUpdate",
    "MessagePublic",
    # Agent
    "Agent",
    "AgentCreate",
    "AgentUpdate",
    "AgentPublic",
    "CustomAgent",
    "CustomAgentCreate",
    "CustomAgentUpdate",
    "CustomAgentPublic",
    # MCP 服务
    "MCPService",
    "MCPServiceCreate",
    "MCPServiceUpdate",
    "MCPServicePublic",
]
