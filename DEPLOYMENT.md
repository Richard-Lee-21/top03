# Top3-Hunter 部署指南

## 生产环境架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端 (Vercel) │    │  后端 (Render)  │    │ 数据库 (Neon)   │
│                 │◄──►│                 │◄──►│                 │
│  - Next.js      │    │  - FastAPI      │    │  - PostgreSQL   │
│  - Edge Runtime │    │  - Python       │    │  - 托管数据库    │
│  - 全球CDN      │    │  - 自动扩展     │    │  - 自动备份     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Redis (Upstash)│
                    │                 │
                    │  - HTTP API     │
                    │  - 全球边缘     │
                    │  - 无服务器     │
                    └─────────────────┘
```

## 部署步骤

### 1. 前端部署 (Vercel)

#### 1.1 准备工作
```bash
# 确保前端项目可以正常构建
cd frontend
npm run build
```

#### 1.2 部署到Vercel
1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 "New Project"
3. 导入GitHub仓库
4. 配置项目设置：
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

#### 1.3 设置环境变量
在Vercel项目设置中添加：
```
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

#### 1.4 自定义域名（可选）
在项目设置中配置自定义域名。

### 2. 后端部署 (Render)

#### 2.1 准备工作
```bash
# 确保后端项目可以正常运行
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 2.2 部署到Render
1. 访问 [Render Dashboard](https://dashboard.render.com)
2. 点击 "New +"
3. 选择 "Web Service"
4. 导入GitHub仓库
5. 配置服务设置：
   - **Name**: top3-hunter-api
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 2.3 设置环境变量
在Render服务设置中添加：
```env
# 应用配置
APP_NAME=Top3-Hunter
DEBUG=false
SECRET_KEY=your-super-secret-production-key

# 数据库配置
DATABASE_URL=postgresql://username:password@host:5432/database

# Redis配置
REDIS_URL=https://your-redis-url.upstash.io

# API密钥
SERPER_API_KEY=your-serper-production-api-key
LLM_API_KEY=your-llm-production-api-key
LLM_PROVIDER=anthropic
LLM_MODEL_NAME=claude-3-haiku-20240307

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-production-password
JWT_SECRET_KEY=your-jwt-production-secret-key

# 缓存配置
CACHE_TTL_QUERY=21600
CACHE_TTL_CONFIG=60
```

#### 2.4 数据库迁移
Render会在部署时自动运行数据库迁移。确保 `alembic` 配置正确。

### 3. 数据库部署 (Neon)

#### 3.1 创建Neon数据库
1. 访问 [Neon Console](https://console.neon.tech)
2. 创建新项目
3. 选择区域（建议选择离用户最近的区域）
4. 复制连接字符串

#### 3.2 配置连接字符串
将Neon提供的连接字符串添加到Render的环境变量中：
```env
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

#### 3.3 数据库备份
Neon自动提供数据库备份功能。在Neon控制台中可以查看和恢复备份。

### 4. Redis部署 (Upstash)

#### 4.1 创建Redis数据库
1. 访问 [Upstash Console](https://console.upstash.com)
2. 创建新Redis数据库
3. 选择区域（建议与应用在同一区域）
4. 复制REST URL和令牌

#### 4.2 配置Redis连接
将Upstash提供的连接信息添加到环境变量中：
```env
REDIS_URL=https://your-redis-url.upstash.io
REDIS_PASSWORD=your-redis-token
```

### 5. API密钥配置

#### 5.1 生产环境API密钥
为生产环境创建专用的API密钥：

**Serper API:**
- 在Serper控制台创建新的生产环境密钥
- 设置更高的配额限制

**LLM API:**
- Claude: 在Anthropic控制台创建生产环境密钥
- OpenAI: 在OpenAI平台创建生产环境密钥

#### 5.2 监控和限制
- 设置API使用限制和告警
- 监控API调用次数和成本
- 实施请求缓存以减少API调用

### 6. 监控和日志

#### 6.1 Vercel监控
- 访问Vercel Analytics查看前端性能
- 配置错误通知

#### 6.2 Render监控
- 查看应用日志和性能指标
- 配置自动重启策略
- 设置健康检查

#### 6.3 自定义监控
```python
# 添加到后端应用
from prometheus_client import Counter, Histogram

# 指标定义
search_requests = Counter('search_requests_total', 'Total search requests')
search_duration = Histogram('search_duration_seconds', 'Search request duration')
```

### 7. 安全配置

#### 7.1 HTTPS和SSL
- 所有服务强制使用HTTPS
- 配置安全头部
- 设置CORS策略

#### 7.2 API安全
- 实施请求频率限制
- 添加API密钥验证
- 监控异常请求

#### 7.3 数据保护
- 加密敏感数据
- 定期更新密钥
- 实施数据备份策略

### 8. 性能优化

#### 8.1 前端优化
- 启用图片优化
- 配置CDN缓存
- 实现代码分割

#### 8.2 后端优化
- 配置数据库连接池
- 启用Redis缓存
- 优化API响应时间

#### 8.3 数据库优化
- 配置适当的索引
- 监控查询性能
- 定期维护数据库

### 9. 故障排除

#### 9.1 常见部署问题

**应用启动失败：**
```bash
# 检查Render日志
# 验证环境变量配置
# 确认依赖包版本
```

**数据库连接问题：**
```bash
# 测试数据库连接
# 检查连接字符串格式
# 验证SSL配置
```

**API调用失败：**
```bash
# 验证API密钥
# 检查网络连接
# 查看服务状态页面
```

#### 9.2 应急响应
- 准备回滚计划
- 建立监控告警
- 制定故障处理流程

### 10. 维护和更新

#### 10.1 部署流程
1. 开发环境测试
2. 预发布环境验证
3. 生产环境部署
4. 部署后验证

#### 10.2 数据库迁移
```bash
# 生成新迁移
alembic revision --autogenerate -m "description"

# 测试迁移
alembic upgrade head

# 部署时自动执行
```

#### 10.3 依赖更新
```bash
# 定期更新依赖
npm audit fix
pip install --upgrade -r requirements.txt
```

## 成本估算

### 月度成本预估
- **Vercel Pro**: $20/月
- **Render**: $7-25/月 (根据使用量)
- **Neon**: $19-99/月 (根据数据库大小)
- **Upstash Redis**: $0-20/月 (根据使用量)
- **API费用**: $10-100/月 (根据调用次数)
- **总计**: $56-264/月

### 成本优化建议
- 使用合适的实例规格
- 优化API调用减少费用
- 利用免费套餐和限额
- 定期审查资源使用情况

这个部署指南涵盖了从开发到生产环境的完整流程，确保Top3-Hunter应用能够稳定、安全、高效地运行。