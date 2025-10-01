# AI API 测试指南

本文档说明如何测试AI相关的API端点，验证其功能和数据库交互。

## 🚀 快速开始

### 1. 环境准备

确保以下服务正在运行：
- **PostgreSQL 数据库** (端口 5432)
- **Python 3.8+**

### 2. 安装依赖

```bash
cd /Users/yeya/FlutterProjects/ai-time/backend
python install_dependencies.py
```

### 3. 初始化数据库

```bash
python init_database.py
```

这将创建以下表：
- `ai_chat_record` - AI聊天记录
- `ai_analysis_record` - AI分析记录
- `ai_recommendation` - AI推荐
- `ai_recommendation_feedback` - 推荐反馈
- `study_methods` - 学习方法
- `method_checkins` - 方法打卡

### 4. 启动服务器

```bash
python start_server.py
```

服务器将在 http://localhost:8000 启动

### 5. 运行API测试

```bash
python test_ai_apis.py
```

## 📋 测试内容

### AI聊天功能
- ✅ 健康检查 (`GET /ai/chat/health`)
- ✅ 发送聊天消息 (`POST /ai/chat`)
- ✅ 获取聊天历史 (`GET /ai/chat/history`)
- ✅ 获取最近聊天历史 (`GET /ai/chat/history/recent`)
- ✅ 获取聊天会话列表 (`GET /ai/chat/sessions`)

### AI推荐功能
- ✅ 学习方法推荐 (`GET /ai/recommendations/method`)
- ✅ 个性化推荐 (`GET /ai/recommendations/personalized`)
- ✅ 推荐反馈 (`POST /ai/recommendations/feedback`)
- ✅ 用户行为分析 (`GET /ai/analysis/user-behavior`)

### 数据库验证
- ✅ 检查表结构
- ✅ 验证记录插入
- ✅ 统计记录数量
- ✅ 查看最新记录

## 🔧 配置说明

### 数据库配置

在 `core/config.py` 中配置PostgreSQL连接：

```python
DATABASE_URL = "postgresql://yeya@localhost:5432/ai_time_management"
```

### AI模型配置

```python
AI_MODEL_API_KEY = "your-api-key"  # 豆包API密钥
AI_MODEL_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
AI_MODEL_NAME = "ep-20241201141448-xxxxxx"  # 模型端点
```

## 📊 测试结果示例

```
🚀 开始 AI API 综合测试
==================================================

🔍 检查数据库表结构...
✅ 表 ai_chat_record 存在，记录数: 0
✅ 表 ai_analysis_record 存在，记录数: 0
✅ 表 ai_recommendation 存在，记录数: 0
✅ 表 ai_recommendation_feedback 存在，记录数: 0
✅ 表 study_methods 存在，记录数: 5
✅ 表 method_checkins 存在，记录数: 0

🔍 测试 AI 聊天健康检查...
✅ 健康检查成功: AI聊天服务正常运行

🔍 测试发送聊天消息...
✅ 聊天消息发送成功
   AI回复: 你好！我是你的AI学习助手...
   会话ID: chat_1_1733123456789
✅ 数据库记录已更新: 0 -> 2
   最新记录: ai - 你好！我是你的AI学习助手，很高兴为你介绍一些有效的学习方法...

==================================================
📊 测试结果总结
==================================================
✅ 通过 健康检查
✅ 通过 发送聊天消息
✅ 通过 获取聊天历史
✅ 通过 获取最近聊天历史
✅ 通过 获取聊天会话列表
✅ 通过 学习方法推荐
✅ 通过 个性化推荐
✅ 通过 推荐反馈
✅ 通过 用户行为分析

总计: 9/9 项测试通过
🎉 所有测试通过！AI API 功能正常
```

## 🛠️ 故障排除

### 1. 数据库连接失败
```
❌ 数据库连接失败: connection to server at "localhost" (::1), port 5432 failed
```

**解决方案：**
- 确保PostgreSQL服务正在运行
- 检查数据库配置是否正确
- 确认用户权限

### 2. 表不存在
```
❌ 表 ai_chat_record 不存在
```

**解决方案：**
```bash
python init_database.py
```

### 3. 依赖包缺失
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案：**
```bash
python install_dependencies.py
```

### 4. 端口被占用
```
❌ 启动服务器失败: [Errno 48] Address already in use
```

**解决方案：**
- 杀死占用端口的进程：`lsof -ti:8000 | xargs kill -9`
- 或修改端口配置

### 5. AI API密钥问题
```
❌ AI服务错误: Unauthorized
```

**解决方案：**
- 检查 `AI_MODEL_API_KEY` 配置
- 确认API密钥有效性
- 检查模型端点配置

## 📝 手动测试

### 使用curl测试

```bash
# 健康检查
curl http://localhost:8000/api/v1/ai/chat/health

# 发送聊天消息
curl -X POST http://localhost:8000/api/v1/ai/chat?user_id=1 \
  -H "Content-Type: application/json" \
  -d '{"content": "你好", "message_type": "text"}'

# 获取聊天历史
curl "http://localhost:8000/api/v1/ai/chat/history?user_id=1&page=1&page_size=10"
```

### 使用浏览器

访问 http://localhost:8000/docs 查看交互式API文档

## 📈 性能监控

### 数据库查询监控

在 `core/database.py` 中启用SQL日志：

```python
engine = create_engine(
    settings.DATABASE_URL,
    echo=True  # 显示SQL查询
)
```

### API响应时间

测试脚本会自动记录每个API的响应时间。

## 🔐 安全注意事项

1. **API密钥安全**：不要在代码中硬编码API密钥
2. **数据库权限**：使用最小权限原则
3. **输入验证**：所有用户输入都经过Pydantic验证
4. **SQL注入防护**：使用参数化查询

## 📞 支持

如果遇到问题，请检查：
1. 服务器日志
2. 数据库连接状态
3. API响应状态码
4. 错误信息详情

测试完成后，您可以确信AI API功能正常工作并与PostgreSQL数据库正确交互！ 