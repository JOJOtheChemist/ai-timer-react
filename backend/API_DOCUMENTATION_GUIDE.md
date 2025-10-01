# 📚 API文档使用指南

## 🎯 快速访问

### API文档已经启动并可访问！

**服务器地址**: `http://localhost:8000`

**三种文档访问方式**:

| 文档类型 | URL | 推荐用途 |
|---------|-----|----------|
| **Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) | 🔥 **推荐** - 交互式测试 |
| **ReDoc** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | 📖 阅读和打印 |
| **OpenAPI JSON** | [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) | 🔧 程序化访问 |

---

## 💡 文档说明

### 什么是API文档？

API文档是FastAPI**自动生成**的，无需手动创建。它包含了所有API端点的完整信息：
- 端点路径和HTTP方法
- 请求参数和格式
- 响应数据结构
- 可交互测试

### 文档来源

文档内容**自动来自**:
1. **路由定义** - `@app.get("/api/...")` 等装饰器
2. **Pydantic模型** - 请求/响应的数据模型
3. **函数文档字符串** - 端点的`"""..."""`注释
4. **类型注解** - Python类型提示

**不需要单独的HTML文件！** FastAPI会根据代码自动生成！

---

## 🚀 如何使用Swagger UI

### 步骤1: 打开文档页面

在浏览器中访问: **http://localhost:8000/docs**

您将看到类似这样的界面:

```
┌────────────────────────────────────────────────────┐
│ AI Time Management API         [Authorize 🔓]     │
│ Version 1.0.0                                      │
├────────────────────────────────────────────────────┤
│ Expand Operations                                  │
│                                                    │
│ ▼ AI聊天                                           │
│   POST /api/v1/ai/chat/message    发送聊天消息     │
│   GET  /api/v1/ai/chat/history    获取聊天历史     │
│                                                    │
│ ▼ AI推荐                                           │
│   GET  /api/v1/ai/recommendations/method           │
│   GET  /api/v1/ai/analysis/user-behavior           │
│                                                    │
│ ▼ 成功案例                                         │
│   GET  /api/v1/cases/hot         获取热门案例      │
│   GET  /api/v1/cases/            案例列表          │
│   GET  /api/v1/cases/search      搜索案例          │
│                                                    │
│ ▼ 系统                                             │
│   GET  /                         根路由            │
│   GET  /health                   健康检查          │
└────────────────────────────────────────────────────┘
```

### 步骤2: 展开查看端点详情

点击任意端点（比如 `GET /api/v1/cases/hot`）展开，您会看到：

```
GET /api/v1/cases/hot

获取热门案例列表

Parameters:
  limit      integer  (query)  返回数量，默认3
  user_id *  integer  (query)  当前用户ID [必需]

Responses:
  200  成功返回案例列表
  422  参数验证错误
```

### 步骤3: 测试API

1. **点击** "Try it out" 按钮
2. **填写** 参数值:
   ```
   limit: 3
   user_id: 1
   ```
3. **点击** "Execute" 按钮执行请求

### 步骤4: 查看响应

执行后会显示:

```
Curl:
curl -X 'GET' \
  'http://localhost:8000/api/v1/cases/hot?limit=3&user_id=1' \
  -H 'accept: application/json'

Request URL:
http://localhost:8000/api/v1/cases/hot?limit=3&user_id=1

Response:
Code: 200
Response body:
[
  {
    "id": 2,
    "title": "如何在职备考CPA并一次通过6科",
    "category": "CPA",
    "view_count": 2300,
    ...
  }
]
```

---

## 📋 当前可用的API端点

### ✅ 已完全可用

#### 1. 系统接口
- `GET /` - 根路由，返回API信息
- `GET /health` - 健康检查

#### 2. AI聊天接口
- `GET /api/v1/ai/chat/health` - 聊天服务健康检查
- `POST /api/v1/ai/chat/message` - 发送消息
- `GET /api/v1/ai/chat/history` - 获取历史记录
- `GET /api/v1/ai/chat/sessions` - 获取会话列表

#### 3. AI推荐接口  
- `GET /api/v1/ai/recommendations/method` - 学习方法推荐
- `GET /api/v1/ai/analysis/user-behavior` - 用户行为分析

### 🔧 已实现但需修复

#### 4. 成功案例接口
- `GET /api/v1/cases/hot` - 获取热门案例 ⚠️
- `GET /api/v1/cases/` - 案例列表（筛选+分页）⚠️
- `GET /api/v1/cases/search` - 搜索案例 ⚠️
- `GET /api/v1/cases/categories` - 获取分类列表 ⚠️
- `GET /api/v1/cases/{case_id}` - 案例详情 ⚠️
- `POST /api/v1/cases/{case_id}/view` - 记录浏览 ⚠️

**注**: 带 ⚠️  的接口代码已实现，但运行时有些小错误需要修复（主要是字段映射问题）

---

## 🎨 Swagger UI 功能特性

### 1. 按模块分组
- 所有端点按功能模块分组（AI聊天、成功案例等）
- 点击模块名可展开/折叠

### 2. 搜索过滤
- 右上角有搜索框
- 可以搜索端点路径、描述、标签

### 3. 模型定义（Schemas）
- 页面底部的 "Schemas" 部分
- 展示所有Pydantic数据模型
- 查看请求/响应的详细结构

### 4. 认证（未实现）
- 右上角的 "Authorize" 按钮
- 生产环境用于JWT Token认证
- 当前版本不需要认证

### 5. 深度链接
- 可以直接链接到特定端点
- 例如: `http://localhost:8000/docs#/AI聊天/send_message`

---

## 📝 测试建议

### 推荐测试流程

```bash
# 1. 健康检查
GET /health

# 2. AI对话（完全可用）
POST /api/v1/ai/chat/message
{
  "content": "你好，请推荐学习方法",
  "session_id": "test-001"
}
参数: user_id=1

# 3. AI推荐（完全可用）
GET /api/v1/ai/recommendations/method?user_id=1&limit=3

# 4. 用户行为分析（完全可用）
GET /api/v1/ai/analysis/user-behavior?user_id=1
```

### 常用测试参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `user_id` | `1` | 测试用户ID |
| `session_id` | `"test-session"` | AI对话会话ID |
| `limit` | `3-10` | 返回数量限制 |
| `page` | `1` | 分页页码 |
| `page_size` | `10` | 每页数量 |

---

## 🔍 ReDoc 使用说明

### 访问地址
http://localhost:8000/redoc

### 特点
- **三栏布局**: 左侧导航、中间内容、右侧示例
- **美观**: 更适合阅读和打印
- **搜索**: 支持全文搜索
- **不可交互**: 仅用于查看，不能直接测试

### 适用场景
- 📖 完整阅读API文档
- 🖨️ 打印文档
- 📧 分享给前端团队
- 📚 学习API设计

---

## 🛠️ OpenAPI JSON

### 访问地址
http://localhost:8000/openapi.json

### 用途
- **代码生成**: 自动生成客户端SDK
- **API测试工具**: 导入Postman、Insomnia
- **CI/CD**: API兼容性检查
- **文档生成**: 生成其他格式文档

### 示例: 导入到Postman

1. 打开Postman
2. 点击 "Import"
3. 选择 "Link"
4. 输入: `http://localhost:8000/openapi.json`
5. 点击 "Continue" 导入

---

## ⚡ 快速命令

### 启动服务器

```bash
cd /Users/yeya/FlutterProjects/ai-time/backend
source venv/bin/activate
python api_server_with_docs.py
```

### 检查服务器状态

```bash
# 健康检查
curl http://localhost:8000/health

# 预期输出:
# {"status":"healthy","message":"API is running","database":"connected"}
```

### 停止服务器

```bash
# 查找进程
lsof -ti :8000

# 停止服务
lsof -ti :8000 | xargs kill -9
```

### 查看日志

```bash
# 实时日志
tail -f api_server.log

# 最近50行
tail -50 api_server.log
```

---

## 📊 数据库测试数据

已插入的测试数据供API测试使用：

### 成功案例 (5条)

| ID | 标题 | 分类 | 价格 | 浏览量 |
|----|------|------|------|--------|
| 1 | 三个月从零基础到通过考研 | 考研 | 199钻石 | 1500 |
| 2 | 如何在职备考CPA并一次通过6科 | CPA | 299钻石 | 2300 |
| 3 | 自学编程转行成功经验分享 | 编程 | 免费 | 1800 |
| 4 | 雅思8分备考攻略 | 英语 | 149钻石 | 1200 |
| 5 | 公务员考试上岸经验 | 公务员 | 199钻石 | 1600 |

---

## 🐛 故障排查

### 问题1: 无法访问 /docs

**检查**:
```bash
# 服务器是否运行？
curl http://localhost:8000/health

# 端口是否被占用？
lsof -i :8000
```

**解决**: 确保服务器正在运行，端口8000可用

### 问题2: API返回404

**原因**: 该端点未注册或模块加载失败

**检查**:
```bash
# 查看服务器日志
cat api_server.log | grep "✅\|⚠️"

# 应该看到:
# ✅ AI聊天模块加载成功
# ✅ AI推荐模块加载成功
# ⚠️ 成功案例模块加载失败: ...
```

### 问题3: API返回422错误

**原因**: 参数验证失败

**解决**: 检查Swagger UI的参数说明，确保提供所有必需参数

### 问题4: API返回500错误

**原因**: 服务器内部错误

**检查**:
```bash
# 查看详细错误日志
cat api_server.log | tail -50
```

---

## 📚 相关文档

| 文档 | 位置 | 说明 |
|------|------|------|
| 启动指南 | `START_SERVER.md` | 服务器启动详细说明 |
| Case API测试报告 | `tests/report/CASE_API_TEST_SUMMARY.md` | Case API测试详情 |
| 测试脚本 | `tests/test_case_apis.py` | 自动化测试脚本 |
| 服务器代码 | `api_server_with_docs.py` | 带文档的完整服务器 |

---

## ✨ 下一步行动

### 为前端开发者

1. ✅ 打开 http://localhost:8000/docs 浏览所有API
2. ✅ 测试AI相关接口（完全可用）
3. ✅ 导出OpenAPI JSON到Postman
4. ✅ 开始集成到前端应用

### 为后端开发者

1. 🔧 修复Case API的字段映射问题
2. 🔧 完善错误处理
3. 🔧 添加JWT认证
4. 🔧 编写单元测试
5. 🔧 添加API限流

---

## 🎉 总结

### ✅ 已完成

- FastAPI自动文档已启用
- Swagger UI可交互测试
- ReDoc美观阅读体验
- OpenAPI JSON可导出
- AI相关API完全可用
- 数据库测试数据已就绪

### 📍 当前状态

- **服务器**: ✅ 运行中 (PID: 75149)
- **端口**: ✅ 8000
- **文档**: ✅ http://localhost:8000/docs
- **AI API**: ✅ 完全可用
- **Case API**: ⚠️ 需要修复

### 🚀 立即开始

**在浏览器打开**: http://localhost:8000/docs

**开始测试您的第一个API!**

---

**文档生成时间**: 2025-10-02  
**API版本**: 1.0.0  
**服务器文件**: `api_server_with_docs.py` 