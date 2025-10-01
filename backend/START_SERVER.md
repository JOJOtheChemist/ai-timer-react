# 🚀 启动API服务器并访问文档

## 📖 API文档访问地址

FastAPI 自动生成三种格式的API文档：

| 文档类型 | 访问地址 | 描述 |
|---------|---------|------|
| **Swagger UI** | `http://localhost:8000/docs` | 交互式API文档，可直接测试 |
| **ReDoc** | `http://localhost:8000/redoc` | 美观的阅读型文档 |
| **OpenAPI JSON** | `http://localhost:8000/openapi.json` | 原始OpenAPI规范 |

---

## 🎯 快速启动

### 方法1: 使用完整服务器（推荐）

```bash
cd /Users/yeya/FlutterProjects/ai-time/backend
source venv/bin/activate
python api_server_with_docs.py
```

然后在浏览器打开：**http://localhost:8000/docs**

### 方法2: 使用测试服务器

```bash
cd /Users/yeya/FlutterProjects/ai-time/backend
source venv/bin/activate
python test_server.py
```

---

## 📚 Swagger UI 功能说明

访问 `http://localhost:8000/docs` 后，您可以：

### 1️⃣ 浏览所有API端点
- 按功能模块分组（AI聊天、AI推荐、成功案例等）
- 查看每个端点的详细说明
- 了解请求参数和响应格式

### 2️⃣ 交互式测试API
1. 点击任意API端点展开详情
2. 点击 **"Try it out"** 按钮
3. 填写必需的参数
4. 点击 **"Execute"** 执行请求
5. 查看实时响应结果

### 3️⃣ 查看数据模型（Schemas）
- 滚动到页面底部
- 查看所有Pydantic数据模型定义
- 了解请求和响应的数据结构

---

## 🎨 文档示例截图说明

### Swagger UI 主界面
```
┌─────────────────────────────────────────────┐
│  AI Time Management API                     │
│  Version 1.0.0                              │
│                                             │
│  ▼ AI聊天                                   │
│    POST /api/v1/ai/chat/message            │
│    GET  /api/v1/ai/chat/history            │
│                                             │
│  ▼ 成功案例                                 │
│    GET  /api/v1/cases/hot                  │
│    GET  /api/v1/cases/                     │
│    GET  /api/v1/cases/search               │
│                                             │
│  [Authorize] 🔓                            │
└─────────────────────────────────────────────┘
```

### 测试API界面
```
POST /api/v1/ai/chat/message
───────────────────────────────────────
Parameters
  user_id *    integer    [输入值: 1]

Request body *   application/json
  {
    "content": "你好",
    "session_id": "test-session"
  }

[Execute] 按钮

Response
  Code: 200
  {
    "content": "你好！我是AI助手...",
    "session_id": "test-session",
    ...
  }
```

---

## 🔧 已实现的API端点

### 🤖 AI功能模块

#### AI聊天 (`/api/v1/ai/chat`)
- `GET /health` - 健康检查
- `POST /message` - 发送消息
- `GET /history` - 获取历史记录
- `GET /sessions` - 获取会话列表
- `DELETE /session/{session_id}` - 删除会话

#### AI推荐 (`/api/v1/ai`)
- `GET /recommendations/method` - 学习方法推荐
- `GET /analysis/user-behavior` - 用户行为分析
- `POST /recommendations/feedback` - 推荐反馈

### 📚 成功案例模块

#### 案例浏览 (`/api/v1/cases`)
- `GET /hot` - 获取热门案例
- `GET /` - 获取案例列表（分页+筛选）
- `GET /search` - 搜索案例
- `GET /categories` - 获取分类列表
- `GET /stats/summary` - 获取统计摘要

#### 案例详情 (`/api/v1/cases`)
- `GET /{case_id}` - 获取案例详情
- `POST /{case_id}/view` - 记录浏览
- `GET /{case_id}/related` - 获取相关案例

#### 案例权限 (`/api/v1/cases`)
- `GET /{case_id}/permission` - 获取权限信息
- `GET /{case_id}/access-status` - 检查访问状态
- `GET /my-purchased` - 获取已购案例

---

## 💡 使用技巧

### 1. 搜索功能
在Swagger UI右上角有搜索框，可以快速查找API端点

### 2. 参数说明
- 带 `*` 的参数是必需的
- 鼠标悬停在参数名上可以看到详细说明
- `query` 参数显示在URL中
- `body` 参数显示在请求体中

### 3. 测试建议
```bash
# 推荐的测试顺序
1. 先测试 GET /health - 确认服务器运行
2. 测试 GET /api/v1/cases/hot - 获取热门案例
3. 测试 POST /api/v1/ai/chat/message - 测试AI对话
4. 测试其他感兴趣的端点
```

### 4. 常见参数
- `user_id`: 大部分接口需要，测试时可用 `1`
- `limit`: 限制返回数量，通常 `3-20`
- `page`: 分页参数，从 `1` 开始
- `page_size`: 每页数量，通常 `10-50`

---

## 🐛 故障排查

### 问题1: 无法访问文档页面

**检查服务器是否运行**:
```bash
curl http://localhost:8000/health
```

**预期输出**:
```json
{"status":"healthy","message":"API is running","database":"connected"}
```

### 问题2: 端口被占用

**查找并关闭占用端口的进程**:
```bash
lsof -ti :8000 | xargs kill -9
```

### 问题3: 数据库连接错误

**检查PostgreSQL服务**:
```bash
psql -U yeya -d ai_time_management -c "SELECT 1;"
```

### 问题4: 模块导入错误

**清理Python缓存**:
```bash
cd /Users/yeya/FlutterProjects/ai-time/backend
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
```

---

## 📊 测试数据

系统已经插入了以下测试数据：

### 成功案例（5条）
1. 三个月从零基础到通过考研（考研，199钻石）
2. 如何在职备考CPA并一次通过6科（CPA，299钻石）
3. 自学编程转行成功经验分享（编程，免费）
4. 雅思8分备考攻略（英语，149钻石）
5. 公务员考试上岸经验（公务员，199钻石）

### AI聊天数据
- 可以直接测试AI对话功能
- 支持多轮对话和上下文理解

---

## 🔐 认证说明

当前版本的API **暂时不需要认证**，所有接口都需要手动传递 `user_id` 参数。

生产环境中应该：
1. 实现JWT Token认证
2. 从Token中解析用户ID
3. 添加权限验证中间件

---

## 📞 技术支持

遇到问题？检查以下资源：

1. **服务器日志**: 查看终端输出的错误信息
2. **数据库日志**: 检查PostgreSQL日志
3. **测试报告**: 查看 `tests/report/` 目录下的测试报告
4. **API响应**: Swagger UI会显示详细的错误信息

---

## ✨ 下一步

完成API测试后，您可以：

1. ✅ 在前端集成这些API
2. ✅ 添加更多测试用例
3. ✅ 实现JWT认证
4. ✅ 添加API限流
5. ✅ 配置生产环境部署

---

**文档更新日期**: 2025-10-02  
**服务器文件**: `api_server_with_docs.py`  
**测试文件目录**: `tests/` 