# AI时间管理系统 - 后端API

## 项目概述

这是AI时间管理系统的后端API，基于FastAPI框架开发，为首页（MainSchedulePage）提供完整的后端服务支持。

## 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy 2.0.23
- **认证**: JWT
- **API文档**: Swagger UI / ReDoc
- **Python版本**: 3.8+

## 项目结构

```
backend/
├── api/v1/                     # API路由
│   ├── endpoints/
│   │   ├── ai/                 # AI相关接口
│   │   ├── task/               # 任务管理接口
│   │   ├── schedule/           # 时间表接口
│   │   └── statistic/          # 统计分析接口
│   └── api.py                  # 主路由
├── core/                       # 核心配置
│   ├── config.py               # 应用配置
│   ├── database.py             # 数据库配置
│   └── dependencies.py         # 依赖注入
├── crud/                       # 数据访问层
│   ├── ai/                     # AI相关CRUD
│   ├── task/                   # 任务相关CRUD
│   ├── schedule/               # 时间表相关CRUD
│   └── statistic/              # 统计相关CRUD
├── models/                     # 数据模型
│   ├── schemas/                # Pydantic模型
│   ├── ai.py                   # AI相关SQLAlchemy模型
│   ├── task.py                 # 任务相关模型
│   └── statistic.py            # 统计相关模型
├── services/                   # 业务逻辑层
│   ├── ai/                     # AI服务
│   ├── task/                   # 任务服务
│   ├── schedule/               # 时间表服务
│   └── statistic/              # 统计服务
├── tests/                      # 测试文件
├── database/                   # 数据库脚本
└── main.py                     # 应用入口
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制配置文件并修改：
```bash
cp config.env.example .env
```

编辑 `.env` 文件，配置数据库连接等信息。

### 3. 初始化数据库

确保PostgreSQL已安装并运行，然后执行数据库脚本：
```bash
cd database
psql ai_time_management -f run_all.sql
```

### 4. 启动服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口说明

### 首页核心功能接口

#### 1. 任务管理 (`/api/v1/tasks`)

- `GET /api/v1/tasks` - 获取任务列表（支持分类筛选）
- `POST /api/v1/tasks` - 创建新任务
- `POST /api/v1/tasks/quick-add` - 快捷创建任务
- `PATCH /api/v1/tasks/{task_id}` - 更新任务
- `PATCH /api/v1/tasks/{task_id}/expand` - 更新任务展开状态
- `DELETE /api/v1/tasks/{task_id}` - 删除任务
- `GET /api/v1/tasks/high-frequency/list` - 获取高频任务
- `GET /api/v1/tasks/overcome/list` - 获取待克服任务

#### 2. 时间表管理 (`/api/v1/schedule`)

- `GET /api/v1/schedule/time-slots` - 获取今日时间表
- `POST /api/v1/schedule/time-slots` - 创建时间段
- `PATCH /api/v1/schedule/time-slots/{slot_id}` - 更新时间段
- `POST /api/v1/schedule/time-slots/{slot_id}/mood` - 提交心情记录
- `POST /api/v1/schedule/time-slots/{slot_id}/task` - 为时段绑定任务
- `PATCH /api/v1/schedule/time-slots/batch/status` - 批量更新状态

#### 3. 统计分析 (`/api/v1/statistics`)

- `GET /api/v1/statistics/weekly-overview` - 获取本周统计概览
- `GET /api/v1/statistics/weekly-chart` - 获取本周图表数据
- `GET /api/v1/statistics/dashboard` - 获取仪表盘数据
- `GET /api/v1/statistics/efficiency-analysis` - 获取效率分析
- `GET /api/v1/statistics/mood-trend` - 获取心情趋势

#### 4. AI功能 (`/api/v1/ai`)

- `POST /api/v1/ai/chat` - AI对话（支持流式响应）
- `GET /api/v1/ai/chat/history` - 获取聊天历史
- `GET /api/v1/ai/schedule-recommendations` - 获取AI推荐
- `POST /api/v1/ai/schedule-recommendations/{rec_id}/accept` - 采纳推荐
- `GET /api/v1/ai/efficiency-tips` - 获取效率建议

## 数据模型

### 核心实体

1. **Task** - 任务
   - 支持分类、类型、高频标记、待克服标记
   - 包含子任务关系

2. **TimeSlot** - 时间段
   - 关联任务和子任务
   - 支持状态管理和心情记录
   - AI推荐标记

3. **MoodRecord** - 心情记录
   - 与时间段一对一关系
   - 支持多种心情类型

4. **StatisticWeekly/Daily** - 统计数据
   - 周/日统计汇总
   - 支持图表数据生成

## 认证授权

目前使用开发模式的用户认证（通过query参数传递user_id）。

生产环境需要：
1. 实现JWT token验证
2. 修改 `core/dependencies.py` 中的认证逻辑
3. 添加用户注册/登录接口

## 测试

运行测试：
```bash
pytest tests/ -v
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t ai-time-backend .

# 运行容器
docker run -p 8000:8000 ai-time-backend
```

### 生产环境配置

1. 设置环境变量
2. 配置反向代理（Nginx）
3. 使用进程管理器（PM2/Supervisor）
4. 配置日志收集
5. 设置监控告警

## 开发指南

### 添加新功能

1. 在 `models/` 中定义数据模型
2. 在 `crud/` 中实现数据访问
3. 在 `services/` 中编写业务逻辑
4. 在 `api/v1/endpoints/` 中创建API接口
5. 在 `tests/` 中添加测试用例

### 代码规范

- 使用类型注解
- 遵循PEP 8规范
- 编写完整的API文档
- 添加适当的错误处理
- 保持代码可测试性

## 常见问题

### Q: 如何添加新的业务域？
A: 按照现有的目录结构，在对应的文件夹中添加新的模块，并在主路由中注册。

### Q: 如何修改数据库模型？
A: 修改SQLAlchemy模型后，使用Alembic生成和应用迁移脚本。

### Q: 如何集成真实的AI服务？
A: 修改 `services/ai/` 中的服务类，替换模拟数据为真实的AI API调用。

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

## 许可证

MIT License 