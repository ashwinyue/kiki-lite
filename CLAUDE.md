# Kiki Lite - 企业级 Agent 脚手架

## 快速开始

```bash
# 安装依赖
uv sync

# 运行开发服务器
uv run uvicorn app.main:app --reload
```

## 项目结构

```
app/
├── agent/          # Agent 核心模块
│   ├── agent.py    # LangGraph Agent (create_react_agent)
│   ├── tools.py    # 工具系统 (@tool 装饰器)
│   └── memory.py   # 记忆管理
├── api/v1/         # API 路由
│   ├── chat.py     # 聊天接口
│   ├── sessions.py # 会话管理
│   └── messages.py # 消息管理
├── config/         # 配置管理
│   ├── settings.py # Pydantic Settings
│   └── dependencies.py
├── llm/            # LLM 服务
│   └── service.py  # DashScope/OpenAI
├── models/         # 数据模型 (SQLModel)
├── repositories/   # 数据访问层
├── observability/  # 可观测性
└── main.py         # 应用入口
```

## 技术栈

- **Web**: FastAPI
- **Agent**: LangGraph + LangChain
- **数据库**: PostgreSQL + SQLModel
- **LLM**: OpenAI / DashScope (阿里通义千问)

## 核心特性

- 工具调用系统 (@tool 装饰器)
- 流式对话响应
- 对话状态管理
- 内存检查点 (LangGraph MemorySaver)
