# fastapi框架重构--》基于ai的OA系统


## ⚙️ 目录说明

```bash
xingoa_back_fastapi/
├── app/
│   ├── api/                # 接口层（请求入口）
│   │   ├── deps/           # 通用依赖（权限校验、数据库连接等）
│   │   └── v1/             # v1 版本 API
│   │       ├── ai/         # AI 功能接口
│   │       │   ├── rag.py  # 文档检索问答接口
│   │       │   └── mcp.py  # 流程自动化接口
│   │       ├── absent.py   # 请假相关接口
│   │       ├── auth.py     # 认证授权接口
│   │       └── ...
│   ├── core/               # 核心配置
│   │   ├── config.py       # 环境变量配置
│   │   ├── security.py     # JWT 工具、密码加密
│   │   └── ai_config.py    # AI 模型配置
│   ├── crud/               # 数据访问层（数据库操作）
│   ├── models/             # 数据库模型（SQLAlchemy ORM）
│   ├── schemas/            # 数据模型（Pydantic 验证）
│   └── services/           # 业务逻辑层
│       └── ai/             # AI 业务逻辑实现
├── ai/                     # AI 核心算法
│   ├── rag/                # 检索增强生成实现
│   └── mcp/                # 流程控制实现
├── db/                     # 数据库初始化
├── alembic/                # 数据库迁移脚本
├── main.py                 # 项目入口
└── requirements.txt        # 依赖清单
```


