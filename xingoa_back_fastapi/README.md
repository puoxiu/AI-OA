# fastapi框架重构--》基于ai的OA系统


xingoa_back_fastapi/
├── app/
│   ├── api/                # 接口层（请求入口）
│   │   ├── deps/           # 通用依赖项，如权限依赖、JWT校验等
│   │   ├── v1/             # 版本1的接口
│   │   │   ├── absent.py   # /absent 相关接口
│   │   │   ├── auth.py     # /auth 登录注册等
│   │   │   └── ...
│   │   └── __init__.py
│   │
│   ├── core/               # 核心配置，如配置文件、初始化逻辑
│   │   ├── config.py       # 读取环境变量配置
│   │   ├── security.py     # JWT工具类、密码哈希等
│   │   └── logging.py      # 日志配置
│   │
│   ├── crud/               # 数据访问层（原DAO），操作数据库模型
│   │   ├── absent.py
│   │   ├── staff.py
│   │   └── ...
│   │
│   ├── models/             # 数据库模型（Pydantic Base + SQLAlchemy ORM）
│   │   ├── absent.py
│   │   ├── staff.py
│   │   └── base.py         # Base = declarative_base()
│   │
│   ├── schemas/            # Pydantic 请求响应数据模型
│   │   ├── absent.py
│   │   ├── staff.py
│   │   └── token.py
│   │
│   ├── services/           # 业务逻辑层（Service Layer）
│   │   ├── absent_service.py
│   │   ├── auth_service.py
│   │   └── ...
│   │
│   ├── deps/               # 通用依赖项（例如：获取db、当前用户）
│   │   └── db.py
│   │
│   ├── db/                 # 数据库初始化与迁移脚本
│   │   ├── base.py         # 将所有 models 统一导入
│   │   ├── session.py      # 连接SessionLocal
│   │   └── init_db.py
│   │
│   ├── main.py             # 项目入口
│   └── __init__.py
│
├── alembic/                # 数据迁移（可选）
├── .env                    # 环境变量配置
├── requirements.txt
└── README.md


## 🧩 对应 Django 中模块的重构建议

| Django 模块目录 | FastAPI 中推荐模块                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------------- |
| absent/     | `app/api/v1/absent.py` + `crud/absent.py` + `schemas/absent.py` + `services/absent_service.py` |
| oaauth/     | `api/v1/auth.py` + `services/auth_service.py` + `schemas/token.py`                             |
| utils/      | `core/` 或 `app/utils/`                                                                         |
| manage.py   | `main.py`                                                                                      |
| settings.py | `core/config.py`                                                                               |
| media/      | `static/` 或直接映射路径                                                                              |
