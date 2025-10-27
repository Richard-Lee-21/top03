# Top3-Hunter 项目设置指南

## 快速开始

### 1. 环境准备

**必需软件：**
- Node.js 18+
- Python 3.9+
- Redis
- PostgreSQL (或使用SQLite进行开发)

### 2. 克隆项目

```bash
git clone <repository-url>
cd top3-hunter
```

### 3. 启动开发环境

```bash
# 启动数据库和Redis
docker-compose up -d

# 安装所有依赖
npm run setup

# 启动开发服务器
npm run dev
```

### 4. 配置API密钥

1. 复制环境配置文件：
```bash
cp backend/.env.example backend/.env
```

2. 编辑 `backend/.env` 文件，填入你的API密钥：
```env
SERPER_API_KEY=your-serper-api-key-here
LLM_API_KEY=your-claude-or-openai-api-key-here
LLM_PROVIDER=anthropic  # 或 openai
LLM_MODEL_NAME=claude-3-haiku-20240307

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password
JWT_SECRET_KEY=your-jwt-secret-key
```

### 5. 初始化数据库

访问管理后台 `http://localhost:3000/admin`，使用管理员账户登录后，点击"初始化种子数据"按钮。

## API密钥获取

### Serper API (搜索服务)
1. 访问 [Serper.dev](https://serper.dev)
2. 注册账户并获取API密钥
3. 免费账户每月有2500次查询额度

### Claude API (Anthropic)
1. 访问 [Anthropic Console](https://console.anthropic.com)
2. 注册账户并创建API密钥
3. 选择合适的模型：claude-3-haiku-20240307 (推荐) 或 claude-3-opus-20240229

### OpenAI API (可选)
1. 访问 [OpenAI Platform](https://platform.openai.com)
2. 注册账户并创建API密钥
3. 推荐使用 gpt-4-turbo-preview 模型

## 开发指南

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

前端运行在 `http://localhost:3000`

### 后端开发

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

后端API运行在 `http://localhost:8000`

API文档：`http://localhost:8000/docs`

### 数据库迁移

```bash
cd backend
alembic upgrade head
```

### 代码格式化

```bash
# 前端
cd frontend && npm run lint

# 后端
cd backend && black app/ && isort app/
```

## 项目结构

```
top3-hunter/
├── frontend/                 # Next.js前端应用
│   ├── src/
│   │   ├── app/             # 页面路由
│   │   ├── components/      # 组件
│   │   ├── lib/            # 工具函数
│   │   └── types/          # 类型定义
│   └── public/             # 静态资源
├── backend/                 # Python FastAPI后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── schemas/        # Pydantic模型
│   ├── alembic/            # 数据库迁移
│   └── main.py             # 应用入口
├── docs/                   # 项目文档
├── docker-compose.yml      # 开发环境
└── README.md
```

## 部署

### 前端部署 (Vercel)

1. 连接GitHub仓库到Vercel
2. 设置环境变量：
   - `NEXT_PUBLIC_API_URL`: 后端API地址

### 后端部署 (Render)

1. 连接GitHub仓库到Render
2. 设置环境变量（同开发环境）
3. 配置PostgreSQL数据库
4. 配置Redis (Upstash)

### 环境变量

**生产环境必需：**
- `DATABASE_URL`: PostgreSQL数据库URL
- `REDIS_URL`: Redis连接URL
- `SERPER_API_KEY`: Serper API密钥
- `LLM_API_KEY`: LLM API密钥
- `SECRET_KEY`: 应用密钥
- `JWT_SECRET_KEY`: JWT密钥
- `ADMIN_PASSWORD`: 管理员密码

## 故障排除

### 常见问题

1. **Redis连接失败**
   ```bash
   # 检查Redis是否运行
   docker-compose ps redis

   # 查看Redis日志
   docker-compose logs redis
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库是否运行
   docker-compose postgres

   # 查看数据库日志
   docker-compose logs postgres
   ```

3. **API密钥错误**
   - 确认API密钥已正确配置在 `.env` 文件中
   - 检查API密钥是否有效且有足够额度

4. **前端无法连接后端**
   - 确认后端服务运行在正确的端口 (8000)
   - 检查CORS配置
   - 确认 `NEXT_PUBLIC_API_URL` 环境变量设置正确

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs frontend
docker-compose logs backend
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交变更
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License