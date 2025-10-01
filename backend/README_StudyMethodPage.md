# 学习方法页（StudyMethodPage）后端API文档

## 概述

根据 `StudyMethodPage.md` 业务域映射表，本文档描述了学习方法页面相关的后端API实现。

## 文件结构

```
backend/
├── api/v1/endpoints/
│   ├── method/
│   │   ├── methods.py            # 学习方法管理
│   │   └── checkins.py           # 方法打卡管理
│   └── ai/
│       └── ai_recommendations.py # AI推荐学习方法
├── services/
│   ├── method/
│   │   ├── method_service.py     # 学习方法业务逻辑
│   │   └── checkin_service.py    # 打卡业务逻辑
│   └── ai/
│       └── ai_recommend_service.py # AI推荐业务逻辑
├── crud/
│   └── method/
│       ├── crud_method.py        # 学习方法数据访问
│       └── crud_checkin.py       # 打卡数据访问
└── models/schemas/
    ├── method.py                 # 学习方法相关模型
    └── ai.py                     # AI推荐相关模型
```

## API端点

### 1. AI推荐学习方法 (`/api/v1/ai/recommendations`)

#### GET `/api/v1/ai/recommendations/method`
- **功能**: 获取针对用户的学习方法推荐
- **参数**: `limit`, `category`
- **响应**: `List[AIStudyMethodResponse]`
- **特点**: 基于时间表数据分析，按"相关性+打卡人数"排序

#### GET `/api/v1/ai/recommendations/method/explain/{method_id}`
- **功能**: 解释为什么推荐某个学习方法
- **响应**: 详细的推荐理由和使用建议

#### GET `/api/v1/ai/recommendations/personalized`
- **功能**: 获取个性化推荐（综合学习方法、任务安排等）
- **响应**: `PersonalizedRecommendationResponse`

#### POST `/api/v1/ai/recommendations/feedback`
- **功能**: 提交推荐反馈，用于改进推荐算法
- **请求体**: 反馈类型、评分、评论

#### GET `/api/v1/ai/analysis/user-behavior`
- **功能**: 获取用户行为分析
- **响应**: 行为标签、分析数据、学习统计

### 2. 学习方法列表展示 (`/api/v1/methods`)

#### GET `/api/v1/methods/`
- **功能**: 获取学习方法列表（支持筛选参数：category）
- **参数**: `category`, `page`, `page_size`
- **响应**: `List[MethodListResponse]`
- **特点**: 自动返回方法的打卡人数、评分

#### GET `/api/v1/methods/{method_id}`
- **功能**: 获取单个学习方法的完整详情
- **响应**: `MethodDetailResponse`
- **包含**: description、steps、scene、meta等

#### GET `/api/v1/methods/popular/trending`
- **功能**: 获取热门学习方法列表（按打卡人数排序）
- **特点**: 使用缓存，每小时更新

#### GET `/api/v1/methods/categories/list`
- **功能**: 获取学习方法分类列表
- **响应**: 分类信息及每个分类的方法数量

#### GET `/api/v1/methods/{method_id}/stats`
- **功能**: 获取学习方法统计信息（打卡人数、评分等）

### 3. 学习方法打卡 (`/api/v1/methods/{method_id}/checkin`)

#### POST `/api/v1/methods/{method_id}/checkin`
- **功能**: 提交学习方法打卡
- **请求体**: `CheckinCreate` (checkin_type、progress、note)
- **响应**: `CheckinResponse`
- **特点**: 校验method_id合法性、进度范围；同步更新方法总打卡数

#### GET `/api/v1/methods/{method_id}/checkins/history`
- **功能**: 查询当前用户的该方法打卡历史
- **参数**: `page`, `page_size`
- **响应**: `List[CheckinHistoryResponse]`

#### GET `/api/v1/methods/{method_id}/checkins/stats`
- **功能**: 获取用户在该方法的打卡统计
- **响应**: 总打卡次数、连续天数、平均进度等

#### PUT `/api/v1/methods/{method_id}/checkins/{checkin_id}`
- **功能**: 更新打卡记录（仅限当天的记录）

#### DELETE `/api/v1/methods/{method_id}/checkins/{checkin_id}`
- **功能**: 删除打卡记录（仅限当天的记录）

#### GET `/api/v1/methods/checkins/calendar`
- **功能**: 获取用户的打卡日历（某月的打卡情况）
- **参数**: `year`, `month`
- **响应**: `CheckinCalendarResponse`

## 数据模型

### 核心响应模型

- `MethodListResponse`: 学习方法列表响应
- `MethodDetailResponse`: 学习方法详情响应
- `CheckinResponse`: 打卡响应
- `AIStudyMethodResponse`: AI推荐学习方法响应

### 请求模型

- `CheckinCreate`: 打卡请求
- `MethodFilterParams`: 筛选参数
- `RecommendationFeedbackRequest`: 推荐反馈请求

### 枚举类型

- `CheckinTypeEnum`: 打卡类型（study, practice, review, complete）
- `DifficultyLevelEnum`: 难度等级（初级、中级、高级、专家级）

## 业务逻辑

### 服务层 (Services)

1. **MethodService**: 处理学习方法相关业务逻辑
   - 方法列表查询和缓存管理
   - 热门方法排序和统计
   - 分类管理和方法筛选

2. **CheckinService**: 处理打卡相关业务逻辑
   - 打卡数据校验和创建
   - 连续打卡天数计算
   - 打卡统计和日历生成

3. **AIRecommendService**: 处理AI推荐相关业务逻辑
   - 用户行为分析
   - 学习方法匹配和推荐
   - 推荐理由生成和解释

### CRUD层

1. **CRUDMethod**: 学习方法数据访问
   - 按分类查询方法
   - 根据用户行为标签匹配方法
   - 热门方法查询和统计更新

2. **CRUDCheckin**: 打卡数据访问
   - 打卡记录的增删改查
   - 打卡统计和历史查询
   - 日期范围和月度统计

## 核心特性

### 1. AI推荐算法

- **用户行为分析**: 基于时间表数据分析学习习惯
- **智能匹配**: 根据行为标签（如"复习不足"）推荐适配方法
- **多维度评分**: 相关性(50%) + 热门度(30%) + 评分(20%)
- **推荐解释**: 生成详细的推荐理由和使用建议

### 2. 缓存优化

- **热门方法缓存**: 1小时有效期，减少数据库压力
- **分层缓存策略**: 列表页缓存 + 详情页实时查询
- **缓存失效机制**: 数据更新时自动刷新缓存

### 3. 打卡数据安全

- **身份验证**: 通过 `get_current_user` 确保用户只能为自己打卡
- **重复校验**: 防止单日重复打卡
- **数据一致性**: 打卡后同步更新方法统计数据

### 4. 统计分析

- **实时统计**: 打卡人数、评分、完成率
- **趋势分析**: 连续打卡天数、月度统计
- **个性化数据**: 用户专属的打卡历史和进度

## 跨域调用逻辑

1. **AI推荐调用方法服务**: `ai_service` → `method_service.get_suitable_by_user_behavior`
2. **打卡同步统计**: `checkin_service` → `statistic_service` → `crud_method.update_checkin_count`
3. **用户行为分析**: `ai_service` → `statistic_service.get_user_study_stats`

## 使用示例

```python
# 获取AI推荐的学习方法
GET /api/v1/ai/recommendations/method?limit=5&category=通用方法

# 获取学习方法列表
GET /api/v1/methods/?category=通用方法&page=1&page_size=20

# 提交学习方法打卡
POST /api/v1/methods/1/checkin
{
    "checkin_type": "study",
    "progress": 80,
    "note": "今天学习了艾宾浩斯遗忘曲线，很有收获",
    "rating": 5
}

# 获取打卡历史
GET /api/v1/methods/1/checkins/history?page=1&page_size=10

# 获取打卡日历
GET /api/v1/methods/checkins/calendar?year=2025&month=1
```

## 扩展功能

### 已实现
- 方法搜索和筛选
- 批量打卡操作
- 数据导出功能
- 推荐反馈系统

### 待扩展
- 方法收藏和分享
- 学习计划生成
- 社交化打卡
- 成就系统集成

## 注意事项

1. **数据库依赖**: 需要创建 `study_methods`、`checkin_records`、`method_categories` 等表
2. **统计服务**: 依赖 `StatisticService` 提供学习统计数据
3. **缓存服务**: 建议使用Redis实现缓存功能
4. **AI算法**: 推荐算法可根据实际效果进行调优
5. **性能优化**: 大量打卡数据建议使用分页和索引优化 