# TutorPage 后端API文档

## 概述

TutorPage（导师页）后端API提供了完整的导师管理功能，包括导师列表展示、详情查看、服务购买、私信沟通和关注管理等核心功能。

## API架构

### 目录结构
```
backend/
├── api/v1/endpoints/tutor/
│   ├── tutors.py              # 导师列表、搜索、统计
│   └── tutor_details.py       # 导师详情、服务、评价
├── services/tutor/
│   ├── tutor_service.py       # 导师业务逻辑
│   └── tutor_detail_service.py # 导师详情业务逻辑
├── crud/tutor/
│   ├── crud_tutor.py          # 导师数据访问
│   ├── crud_tutor_review.py   # 导师评价数据访问
│   └── crud_tutor_service_order.py # 导师服务订单数据访问
└── models/schemas/
    ├── tutor.py               # 导师相关数据模型
    └── user.py                # 用户相关扩展模型
```

## 核心API端点

### 1. 导师管理 (`/api/v1/tutors`)

#### 1.1 获取导师列表
- **端点**: `GET /api/v1/tutors/`
- **功能**: 获取导师列表，支持筛选和排序
- **参数**:
  - `tutor_type`: 导师类型筛选
  - `domain`: 擅长领域筛选
  - `price_range`: 价格区间筛选
  - `sort_by`: 排序方式（rating/price/experience）
  - `page`: 页码
  - `page_size`: 每页数量
- **响应**: `List[TutorListResponse]`

#### 1.2 搜索导师
- **端点**: `GET /api/v1/tutors/search`
- **功能**: 按关键词搜索导师（匹配姓名、擅长领域）
- **参数**:
  - `keyword`: 搜索关键词
  - `page`: 页码
  - `page_size`: 每页数量
- **响应**: `List[TutorSearchResponse]`

#### 1.3 获取导师领域列表
- **端点**: `GET /api/v1/tutors/domains`
- **功能**: 获取所有导师擅长领域列表
- **响应**: `List[str]`

#### 1.4 获取导师类型列表
- **端点**: `GET /api/v1/tutors/types`
- **功能**: 获取所有导师类型列表
- **响应**: `List[str]`

#### 1.5 获取导师统计摘要
- **端点**: `GET /api/v1/tutors/stats/summary`
- **功能**: 获取导师统计摘要（总数、类型统计等）
- **响应**: `TutorStatsResponse`

#### 1.6 获取热门推荐导师
- **端点**: `GET /api/v1/tutors/popular`
- **功能**: 获取热门推荐导师
- **参数**:
  - `limit`: 推荐数量（默认5）
- **响应**: `List[TutorListResponse]`

### 2. 导师详情 (`/api/v1/tutors/{tutor_id}`)

#### 2.1 获取导师详情
- **端点**: `GET /api/v1/tutors/{tutor_id}`
- **功能**: 获取单个导师的完整详情
- **响应**: `TutorDetailResponse`

#### 2.2 获取导师服务列表
- **端点**: `GET /api/v1/tutors/{tutor_id}/services`
- **功能**: 获取导师的服务列表
- **响应**: `List[TutorServiceResponse]`

#### 2.3 获取导师评价列表
- **端点**: `GET /api/v1/tutors/{tutor_id}/reviews`
- **功能**: 获取导师的学员评价列表
- **参数**:
  - `page`: 页码
  - `page_size`: 每页数量
- **响应**: `List[TutorReviewResponse]`

#### 2.4 获取导师数据面板
- **端点**: `GET /api/v1/tutors/{tutor_id}/metrics`
- **功能**: 获取导师的指导数据面板
- **响应**: `TutorMetricsResponse`

#### 2.5 记录导师浏览
- **端点**: `POST /api/v1/tutors/{tutor_id}/view`
- **功能**: 记录导师页面浏览次数
- **响应**: `{"message": "浏览记录已更新"}`

#### 2.6 获取相似导师
- **端点**: `GET /api/v1/tutors/{tutor_id}/similar`
- **功能**: 获取相似推荐导师
- **参数**:
  - `limit`: 推荐数量（默认5）
- **响应**: `List[TutorListResponse]`

### 3. 用户资产扩展 (`/api/v1/users/me/assets`)

#### 3.1 购买导师服务
- **端点**: `POST /api/v1/users/me/assets/purchase`
- **功能**: 提交导师服务购买请求
- **请求体**: `TutorServicePurchaseCreate`
- **响应**: `TutorServiceOrderResponse`

#### 3.2 获取导师服务订单历史
- **端点**: `GET /api/v1/users/me/orders/tutor`
- **功能**: 查询用户的导师服务订单历史
- **参数**:
  - `page`: 页码
  - `page_size`: 每页数量
- **响应**: `List[TutorServiceOrderResponse]`

### 4. 用户关系扩展 (`/api/v1/users/me/relations`)

#### 4.1 向导师发送私信
- **端点**: `POST /api/v1/users/me/relations/message/tutor/{tutor_id}`
- **功能**: 向指定导师发送私信
- **请求体**: `PrivateMessageCreate`
- **响应**: `PrivateMessageResponse`

#### 4.2 关注导师
- **端点**: `POST /api/v1/users/me/relations/follow/tutor/{tutor_id}`
- **功能**: 关注指定导师
- **响应**: `FollowResponse`

#### 4.3 取消关注导师
- **端点**: `DELETE /api/v1/users/me/relations/follow/tutor/{tutor_id}`
- **功能**: 取消关注导师
- **响应**: `FollowResponse`

#### 4.4 获取关注的导师列表
- **端点**: `GET /api/v1/users/me/relations/follow/tutors`
- **功能**: 查询用户关注的导师列表
- **参数**:
  - `page`: 页码
  - `page_size`: 每页数量
- **响应**: `List[FollowedTutorResponse]`

## 数据模型

### 核心响应模型

#### TutorListResponse
```python
{
    "id": int,
    "name": str,
    "avatar": str,
    "title": str,
    "tutor_type": str,
    "domains": List[str],
    "experience_years": int,
    "rating": float,
    "review_count": int,
    "student_count": int,
    "price_range": str,
    "is_verified": bool,
    "is_online": bool,
    "response_rate": float,
    "service_summary": str,
    "created_at": datetime,
    "updated_at": datetime
}
```

#### TutorDetailResponse
```python
{
    "id": int,
    "name": str,
    "avatar": str,
    "title": str,
    "bio": str,
    "tutor_type": str,
    "domains": List[str],
    "experience_years": int,
    "education_background": str,
    "certifications": List[str],
    "rating": float,
    "review_count": int,
    "student_count": int,
    "success_rate": float,
    "response_rate": float,
    "response_time": str,
    "is_verified": bool,
    "is_online": bool,
    "last_active": datetime,
    "service_details": List[dict],
    "data_panel": dict,
    "reviews": List[dict],
    "is_followed": bool,
    "created_at": datetime,
    "updated_at": datetime
}
```

#### TutorServiceOrderResponse
```python
{
    "order_id": str,
    "user_id": int,
    "tutor_id": int,
    "service_id": int,
    "service_name": str,
    "amount": float,
    "currency": str,
    "status": str,
    "created_at": datetime
}
```

## 业务逻辑

### 1. 导师筛选和搜索
- 支持按导师类型、擅长领域、价格区间进行筛选
- 支持按评分、价格、经验年限进行排序
- 关键词搜索匹配导师姓名、头衔、领域和简介

### 2. 导师服务购买流程
1. 获取服务价格信息（防止前端篡改）
2. 校验用户钻石余额
3. 扣减钻石（数据库事务保证原子性）
4. 创建服务订单
5. 更新导师相关统计

### 3. 导师关注机制
- 用户可以关注/取消关注导师
- 关注操作会同步更新导师粉丝数
- 支持查询用户关注的导师列表

### 4. 私信功能
- 用户可以向导师发送私信
- 校验导师存在性
- 触发消息提醒机制

### 5. 浏览统计
- 记录用户对导师页面的浏览
- 防止重复计数（每日一次）
- 更新导师浏览量统计

## 跨域调用处理

### 1. 服务购买时的价格校验
```python
# user_asset_service调用tutor_service
service_price = await self.tutor_service.get_tutor_service_price(tutor_id, service_id)
```

### 2. 关注导师时的粉丝数更新
```python
# user_relation_service调用tutor_service
await self.tutor_service.update_tutor_fan_count(tutor_id, increment=1)
```

### 3. 导师基础信息获取
```python
# user_relation_service调用tutor_service
tutor_info = await self.tutor_service.get_tutor_basic_info(tutor_id)
```

## 数据一致性保障

### 1. 服务购买事务
- 钻石扣减与订单创建在同一事务中
- 确保"钻石扣减成功则订单必生成，订单失败则钻石不扣减"

### 2. 关注关系唯一性
- 通过`user_id+tutor_id`唯一约束避免重复关注
- 粉丝数通过"更新计数器"而非实时统计，提升查询效率

### 3. 浏览记录防重复
- 每日每用户对每导师只记录一次浏览
- 通过日期+用户ID+导师ID的组合键保证唯一性

## 缓存策略

### 1. 热门导师缓存
- 缓存热门导师列表（按评分和学生数排序）
- 缓存时间：30分钟
- 缓存键：`popular_tutors:{limit}`

### 2. 导师统计缓存
- 缓存导师统计摘要数据
- 缓存时间：1小时
- 缓存键：`tutor_stats_summary`

### 3. 导师领域和类型缓存
- 缓存所有导师领域和类型列表
- 缓存时间：6小时
- 缓存键：`tutor_domains`, `tutor_types`

## 错误处理

### 1. 导师不存在
- HTTP 404: 导师不存在或已被禁用

### 2. 服务购买失败
- HTTP 400: 钻石余额不足
- HTTP 404: 服务不存在或不可用
- HTTP 500: 支付处理失败

### 3. 关注操作失败
- HTTP 404: 导师不存在
- HTTP 400: 已关注此导师（重复关注）

### 4. 私信发送失败
- HTTP 404: 导师不存在
- HTTP 400: 消息内容为空或过长

## 性能优化

### 1. 数据库查询优化
- 导师列表查询使用索引（tutor_type, domains, rating）
- 搜索查询使用全文索引
- 分页查询使用LIMIT/OFFSET

### 2. 关联查询优化
- 导师详情页面使用JOIN查询减少数据库往返
- 评价列表使用分页加载
- 服务列表按可用性筛选

### 3. 缓存使用
- 热门数据使用Redis缓存
- 静态数据（领域、类型）长期缓存
- 用户个性化数据短期缓存

## 安全考虑

### 1. 权限控制
- 所有API需要用户认证
- 导师信息修改需要导师身份验证
- 敏感操作（购买、私信）需要额外验证

### 2. 数据校验
- 服务价格从后端获取，防止前端篡改
- 用户输入严格校验和过滤
- SQL注入防护

### 3. 频率限制
- 私信发送频率限制
- 搜索请求频率限制
- 浏览记录防刷机制

## 监控和日志

### 1. 关键指标监控
- 导师服务购买成功率
- 导师页面访问量
- 私信发送成功率
- 关注/取消关注操作量

### 2. 业务日志
- 服务购买流程日志
- 导师关注操作日志
- 私信发送日志
- 异常错误日志

### 3. 性能监控
- API响应时间
- 数据库查询性能
- 缓存命中率
- 系统资源使用率 