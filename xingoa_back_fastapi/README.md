# fastapi框架重构--》基于ai的OA系统


## 🧩 对应 Django 中模块的重构建议

| Django 模块目录 | FastAPI 中推荐模块                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------------- |
| absent/     | `app/api/v1/absent.py` + `crud/absent.py` + `schemas/absent.py` + `services/absent_service.py` |
| oaauth/     | `api/v1/auth.py` + `services/auth_service.py` + `schemas/token.py`                             |
| utils/      | `core/` 或 `app/utils/`                                                                         |
| manage.py   | `main.py`                                                                                      |
| settings.py | `core/config.py`                                                                               |
| media/      | `static/` 或直接映射路径                                                                              |




xingoa_back_fastapi/
├── app/
│   ├── api/                # 接口层（请求入口）
│   │   ├── deps/           # 通用依赖项，如权限依赖、JWT 校验等
│   │   │   └── __init__.py
│   │   ├── v1/             # 版本 1 的接口
│   │   │   ├── absent.py   # /absent 相关接口
│   │   │   ├── auth.py     # /auth 登录注册等
│   │   │   ├── inform.py   # /inform 通知相关接口
│   │   │   ├── staff.py    # /staff 员工相关接口
│   │   │   ├── ai/         # AI 相关接口
│   │   │   │   ├── rag.py  # RAG 相关接口
│   │   │   │   └── mcp.py  # MCP 相关接口
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/               # 核心配置，如配置文件、初始化逻辑
│   │   ├── config.py       # 读取环境变量配置
│   │   ├── security.py     # JWT 工具类、密码哈希等
│   │   ├── logging.py      # 日志配置
│   │   ├── ai_config.py    # AI 相关配置
│   │   └── __init__.py
│   ├── crud/               # 数据访问层（原 DAO），操作数据库模型
│   │   ├── absent.py
│   │   ├── staff.py
│   │   ├── inform.py
│   │   └── __init__.py
│   ├── models/             # 数据库模型（Pydantic Base + SQLAlchemy ORM）
│   │   ├── absent.py
│   │   ├── staff.py
│   │   ├── inform.py
│   │   ├── base.py         # Base = declarative_base()
│   │   └── __init__.py
│   ├── schemas/            # Pydantic 请求响应数据模型
│   │   ├── absent.py
│   │   ├── staff.py
│   │   ├── inform.py
│   │   ├── token.py
│   │   ├── ai/             # AI 相关数据模型
│   │   │   ├── rag.py      # RAG 相关数据模型
│   │   │   └── mcp.py      # MCP 相关数据模型
│   │   └── __init__.py
│   ├── services/           # 业务逻辑层（Service Layer）
│   │   ├── absent_service.py
│   │   ├── auth_service.py
│   │   ├── inform_service.py
│   │   ├── staff_service.py
│   │   ├── ai/             # AI 相关业务逻辑
│   │   │   ├── rag_service.py  # RAG 相关业务逻辑
│   │   │   └── mcp_service.py  # MCP 相关业务逻辑
│   │   └── __init__.py
│   └── __init__.py
├── deps/                   # 通用依赖项（例如：获取 db、当前用户）
│   └── db.py
├── db/                     # 数据库初始化与迁移脚本
│   ├── base.py             # 将所有 models 统一导入
│   ├── session.py          # 连接 SessionLocal
│   ├── init_db.py
│   └── __init__.py
├── alembic/                # 数据迁移（可选）
│   ├── env.py
│   ├── versions/
│   │   └── ...
│   └── ...
├── ai/                     # AI 相关核心代码
│   ├── rag/                # RAG 相关代码
│   │   ├── retriever.py    # 检索器
│   │   ├── generator.py    # 生成器
│   │   └── __init__.py
│   ├── mcp/                # MCP 相关代码
│   │   ├── processor.py    # 处理器
│   │   └── __init__.py
│   └── __init__.py
├── .env                    # 环境变量配置
├── requirements.txt
├── main.py                 # 项目入口
└── README.md