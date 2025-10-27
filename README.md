# Top3-Hunter: 动态商品推荐引擎

一个基于实时网络搜索和AI分析的智能商品推荐系统，用户输入商品关键词即可获得全网综合推荐度最高的Top3商品。

## 🚀 核心特性

- **实时搜索**: 集成Serper.dev API获取最新商品信息
- **AI分析**: 使用Claude/OpenAI等大语言模型进行智能分析
- **动态配置**: 管理后台可实时调整API密钥和提示词
- **缓存优化**: Redis缓存提升响应速度
- **响应式设计**: 支持多端设备访问

## 🏗️ 技术架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Next.js) │    │  后端 (FastAPI) │    │   数据库 (PG)   │
│                 │◄──►│                 │◄──►│                 │
│  - 用户界面      │    │  - API端点      │    │  - 配置存储      │
│  - 管理后台      │    │  - 搜索集成     │    │  - 缓存管理      │
│  - 响应式设计    │    │  - LLM分析      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   外部服务       │
                    │                 │
                    │  - Serper搜索   │
                    │  - Claude/OpenAI│
                    │  - Redis缓存    │
                    └─────────────────┘
```

## 📁 项目结构

```
top3-hunter/
├── frontend/                 # Next.js前端应用
│   ├── src/
│   │   ├── app/             # App Router页面
│   │   ├── components/      # 组件库
│   │   ├── lib/            # 工具函数
│   │   └── types/          # TypeScript类型定义
│   ├── public/             # 静态资源
│   └── package.json
├── backend/                 # Python FastAPI后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── alembic/            # 数据库迁移
│   ├── requirements.txt
│   └── main.py
├── docs/                   # 项目文档
├── docker-compose.yml      # 本地开发环境
├── README.md
└── .gitignore
```

## 🛠️ 开发环境搭建

### 前置要求
- Node.js 18+
- Python 3.9+
- Redis
- PostgreSQL

### 本地开发
```bash
# 克隆项目
git clone <repository-url>
cd top3-hunter

# 启动开发环境
docker-compose up -d

# 安装前端依赖
cd frontend
npm install
npm run dev

# 安装后端依赖
cd ../backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## 📚 API文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看完整的API文档。

## 🚀 部署

- **前端**: Vercel
- **后端**: Render
- **数据库**: Neon/Supabase
- **缓存**: Redis (Upstash)

## 📄 许可证

MIT License