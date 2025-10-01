# 个人主页（PersonalPage）后端API文档

## 概述

根据 `PersonalPage.md` 业务域映射表，本文档描述了个人主页相关的后端API实现。

## 文件结构

```
backend/
├── api/v1/endpoints/
│   ├── user/
│   │   ├── user_profiles.py      # 个人信息管理
│   │   ├── user_assets.py        # 资产管理
│   │   ├── user_relations.py     # 关系链管理
│   │   └── personal_page.py      # 综合个人主页
│   └── badge/
│       └── badges.py             # 徽章管理
├── services/
│   ├── user/
│   │   ├── user_profile_service.py
│   │   ├── user_asset_service.py
│   │   └── user_relation_service.py
│   └── badge/
│       └── badge_service.py
└── crud/
    ├── user/
    │   ├── crud_user_profile.py
    │   ├── crud_user_asset.py
    │   └── crud_user_relation.py
    └── badge/
        └── crud_badge.py
```

## API端点

### 1. 个人信息管理 (`/api/v1/users/me/profile`)

#### GET `/api/v1/users/me/profile`
- **功能**: 获取当前登录用户的完整个人信息
- **响应**: `UserProfileResponse`
- **包含**: 基础信息、总学习时长、动态数、徽章数等

#### PUT `/api/v1/users/me/profile`
- **功能**: 更新当前用户的个人信息
- **请求体**: `UserProfileUpdate`
- **响应**: `UserOperationResponse`

### 2. 资产管理 (`/api/v1/users/me/assets`)

#### GET `/api/v1/users/me/assets`
- **功能**: 获取当前用户的资产信息
- **响应**: `UserAssetResponse`
- **包含**: 钻石数量、消费记录等

#### POST `/api/v1/users/me/assets/recharge`
- **功能**: 发起钻石充值请求
- **请求体**: `RechargeRequest`
- **响应**: `RechargeResponse`

#### GET `/api/v1/users/me/assets/records`
- **功能**: 获取用户资产变动记录
- **响应**: `List[AssetRecordResponse]`

### 3. 关系链管理 (`/api/v1/users/me/relations`)

#### GET `/api/v1/users/me/relations/stats`
- **功能**: 获取用户关系统计
- **响应**: `RelationStatsResponse`
- **包含**: 关注导师数、粉丝数等

#### GET `/api/v1/users/me/relations/tutors`
- **功能**: 获取用户关注的导师列表
- **参数**: `limit`, `offset`
- **响应**: `FollowedTutorResponse`

#### GET `/api/v1/users/me/relations/fans`
- **功能**: 获取用户的最近粉丝列表
- **参数**: `limit`, `offset`
- **响应**: `RecentFanResponse`

#### POST `/api/v1/users/me/relations/follow/{target_user_id}`
- **功能**: 关注用户
- **响应**: `UserOperationResponse`

#### DELETE `/api/v1/users/me/relations/unfollow/{target_user_id}`
- **功能**: 取消关注用户
- **响应**: `UserOperationResponse`

### 4. 徽章系统 (`/api/v1/badges`)

#### GET `/api/v1/badges/my`
- **功能**: 获取当前用户的徽章列表
- **参数**: `category` (可选)
- **响应**: `UserBadgeListResponse`

#### GET `/api/v1/badges/{badge_id}`
- **功能**: 获取单个徽章的详情
- **响应**: `BadgeDetailResponse`

#### GET `/api/v1/badges/`
- **功能**: 获取所有徽章列表
- **参数**: `category`, `limit`, `offset`
- **响应**: `List[BadgeDetailResponse]`

#### PUT `/api/v1/badges/display`
- **功能**: 更新徽章展示设置
- **请求体**: `List[BadgeDisplayUpdate]`
- **响应**: `BadgeOperationResponse`

#### GET `/api/v1/badges/display/current`
- **功能**: 获取当前展示的徽章列表
- **响应**: `BadgeDisplayResponse`

### 5. 综合个人主页 (`/api/v1/users/me`)

#### GET `/api/v1/users/me/personal-page`
- **功能**: 获取个人主页综合数据
- **响应**: `PersonalPageResponse`
- **包含**: 个人信息、资产、关系、统计等所有数据

#### GET `/api/v1/users/me/dashboard-summary`
- **功能**: 获取个人主页仪表板摘要数据（轻量级）
- **响应**: 包含用户基础信息、快速统计、最近徽章、快捷操作等

## 数据模型

### 核心响应模型

- `UserProfileResponse`: 用户个人信息响应
- `UserAssetResponse`: 用户资产响应
- `RelationStatsResponse`: 关系统计响应
- `UserBadgeListResponse`: 用户徽章列表响应
- `PersonalPageResponse`: 个人主页综合响应

### 请求模型

- `UserProfileUpdate`: 用户信息更新请求
- `RechargeRequest`: 充值请求
- `BadgeDisplayUpdate`: 徽章展示设置更新

## 业务逻辑

### 服务层 (Services)

1. **UserProfileService**: 处理用户个人信息相关业务逻辑
   - 数据校验（邮箱格式、手机号格式、用户名唯一性）
   - 关联数据获取（学习时长、动态数、徽章数）

2. **UserAssetService**: 处理用户资产相关业务逻辑
   - 充值订单生成
   - 支付回调处理
   - 资产变动记录

3. **UserRelationService**: 处理用户关系链相关业务逻辑
   - 关系统计计算
   - 关注/取消关注操作
   - 粉丝和关注列表管理

4. **BadgeService**: 处理徽章系统相关业务逻辑
   - 徽章进度计算
   - 解锁条件判断
   - 展示设置管理

### CRUD层

每个服务都有对应的CRUD层，负责数据库操作：
- 查询、创建、更新、删除操作
- 数据转换和映射
- 事务管理

## 安全性

- 所有接口都使用 `/me/` 前缀，确保只能访问当前登录用户的数据
- 依赖注入 `get_current_user` 进行身份验证
- 数据校验和异常处理

## 扩展性

- 模块化设计，易于添加新功能
- 服务层抽象，便于业务逻辑扩展
- 统一的错误处理和响应格式

## 使用示例

```python
# 获取个人主页综合数据
GET /api/v1/users/me/personal-page

# 更新个人信息
PUT /api/v1/users/me/profile
{
    "username": "new_username",
    "goal": "考研上岸",
    "bio": "努力学习中..."
}

# 充值钻石
POST /api/v1/users/me/assets/recharge
{
    "amount": 100.00,
    "payment_method": "alipay"
}

# 获取徽章列表
GET /api/v1/badges/my?category=study
```

## 注意事项

1. 部分功能依赖其他服务（如统计服务、动态服务），需要在实际部署时确保服务间通信正常
2. 数据库表结构需要根据SQL文件创建
3. 支付功能需要对接实际的支付平台
4. 建议使用Redis等缓存来提高性能 