# 前端API路径修复说明

## 问题描述
首页无法访问，后端日志显示大量404错误，原因是API路径出现重复的 `/v1`。

## 问题根源
- `api.js` 中的 `API_BASE_URL` 设置为 `http://localhost:8000/api/v1`
- 但各个服务文件（如 `scheduleService.js`）中的路径仍然包含 `/v1/`
- 导致最终URL变成：`http://localhost:8000/api/v1/v1/tasks`（重复的v1）

## 已完成的修复

### 1. 修复的服务文件
✅ `scheduleService.js` - 所有 `/v1/` 路径改为 `/`
✅ `methodService.js` - 所有 `/v1/` 路径改为 `/`  
✅ `tutorService.js` - 所有 `/v1/` 路径改为 `/`
✅ `successService.js` - 所有 `/v1/` 路径改为 `/`
✅ `aiService.js` - 所有 `/v1/` 路径改为 `/`
✅ `taskService.js` - 所有 `/v1/` 路径改为 `/`

### 2. 服务器状态
✅ 后端服务器运行中 (端口 8000)
✅ 前端服务器运行中 (端口 3000)

## 下一步操作

### 1. 清除浏览器缓存
**非常重要！** 需要清除浏览器缓存才能加载新的代码：

**Chrome/Edge:**
- 按 `Cmd + Shift + Delete` (Mac) 或 `Ctrl + Shift + Delete` (Windows)
- 选择"缓存的图像和文件"
- 点击"清除数据"
- 或直接按 `Cmd/Ctrl + Shift + R` 强制刷新

**Safari:**
- 按 `Cmd + Option + E` 清空缓存
- 然后 `Cmd + R` 刷新

### 2. 访问首页
打开浏览器访问：
```
http://localhost:3000/schedule
```

### 3. 检查其他页面
所有页面现在都应该可以正常访问：
- `/schedule` - 时间表主页
- `/study-methods` - 学习方法页
- `/tutors` - 导师推荐页  
- `/success` - 成功案例页
- `/moments` - 动态广场
- `/messages` - 消息页
- `/personal` - 个人主页

## 数据说明
所有测试数据都已绑定到 **user 101**：
- ✅ 时间表任务和时间段
- ✅ 学习方法（5个）
- ✅ 导师信息（4位导师，每位3项服务）
- ✅ 成功案例（5个）
- ✅ 动态内容（10条）
- ✅ 消息记录（10条）

## 故障排除

### 如果仍然看到404错误：
1. **清除浏览器缓存**（最重要！）
2. **检查Network面板**：看请求的URL是否还包含 `/v1/v1`
3. **重启前端服务器**：
   ```bash
   # 停止前端服务器
   pkill -f "react-scripts"
   
   # 重新启动
   cd /Users/yeya/FlutterProjects/ai-time/frontend
   npm start
   ```

### 如果看到空数据：
检查前端代码中的 `USER_ID` 变量：
- 应该设置为 `101` 而不是 `1`
- 主要检查这些文件：
  - `MainSchedulePage.jsx`
  - `StudyMethodPage.jsx`
  - `TutorPage.jsx`
  - `SuccessPage.jsx`

## 验证修复成功
修复成功后，后端日志应该显示类似这样的请求：
```
INFO: "GET /api/v1/tasks?user_id=101 HTTP/1.1" 200 OK
INFO: "GET /api/v1/schedule/time-slots?user_id=101 HTTP/1.1" 200 OK
INFO: "GET /api/v1/methods/?user_id=101 HTTP/1.1" 200 OK
```

注意：
- ✅ 只有一个 `/v1`
- ✅ user_id=101
- ✅ 返回 200 OK

---

**修复时间**: 2025-10-02
**修复人员**: AI Assistant 