# User Profiles API 分析报告

**分析时间**: 2025-10-02  
**分析范围**: 用户个人信息API (`/api/v1/users/me/profile`, `/api/v1/users/{user_id}/simple-info`)  
**状态**: ⚠️ **需要修复 - Schema不匹配**

---

## 📊 测试结果

| 测试项 | 状态 | 说明 |
|--------|------|------|
| 数据库连接 | ✅ 通过 | PostgreSQL连接正常 |
| 数据库数据完整性 | ✅ 通过 | user和user_profile表数据正常 |
| API端点测试 | ⚠️ 跳过 | 需要认证中间件 |
| CRUD层验证 | ❌ 需修复 | 表名和字段不匹配 |

---

## 🔍 发现的问题

### 1. **数据库Schema不匹配**

#### 实际数据库结构：

**`user` 表** (基础用户信息):
```sql
- id (bigint, PK)
- username (varchar(50))
- avatar (varchar(255))
- phone (varchar(20), unique)
- password_hash (varchar(255))
- goal (varchar(100))
- major (varchar(50))
- join_time (timestamp)
- status (smallint)
- created_at (timestamp)
- updated_at (timestamp)
```

**`user_profile` 表** (扩展用户信息):
```sql
- id (bigint, PK)
- user_id (bigint, unique, FK to user.id)
- real_name (varchar(50))
- bio (text)
- total_study_hours (numeric(10,1))
- created_at (timestamp)
- updated_at (timestamp)
```

#### CRUD层引用的表结构（错误）:

**`user_profiles` 表** (不存在，应该是`user_profile`):
```python
# crud/user/crud_user_profile.py - 错误引用
query = """
SELECT 
    user_id, username, nickname, avatar, email, phone, 
    goal, bio, is_public, allow_follow, create_time, update_time
FROM user_profiles  # ❌ 表名错误
WHERE user_id = :user_id
"""
```

#### 字段不匹配：

| CRUD引用字段 | 实际数据库字段 | 所在表 | 状态 |
|-------------|--------------|--------|------|
| `nickname` | ❌ 不存在 | - | 需移除或映射 |
| `email` | ❌ 不存在 | - | 需移除 |
| `is_public` | ❌ 不存在 | - | 需移除 |
| `allow_follow` | ❌ 不存在 | - | 需移除 |
| `create_time` | `created_at` | user_profile | 需修正 |
| `update_time` | `updated_at` | user_profile | 需修正 |
| - | `real_name` ✅ | user_profile | 缺失引用 |
| `username` ✅ | `username` | user | 正确 |
| `avatar` ✅ | `avatar` | user | 正确 |
| `phone` ✅ | `phone` | user | 正确 |
| `goal` ✅ | `goal` | user | 正确 |
| `bio` ✅ | `bio` | user_profile | 正确 |

### 2. **认证中间件未实现**

API端点使用了 `get_current_user` 依赖，但该依赖未实现或未正确配置。

**相关代码**:
```python
# api/v1/endpoints/user/user_profiles.py
from core.dependencies import get_db, get_current_user

@router.get("/me/profile")
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),  # ❌ 未实现
    db: Session = Depends(get_db)
):
```

### 3. **Service层依赖外部服务**

UserProfileService 依赖其他未完成的服务：

```python
# services/user/user_profile_service.py
# 依赖 StatisticService (已实现)
study_stats = await self.statistic_service.get_user_study_stats(user_id)

# 依赖 Moment服务 (暂未实现，返回0)
moment_count = await self._get_user_moment_count(user_id)

# 依赖 Badge服务 (暂未实现，返回0)
badge_count = await self._get_user_badge_count(user_id)
```

---

## 🔧 需要修复的内容

### 优先级1: CRUD层修复

1. **修正表名**:
   - `user_profiles` → `user_profile`

2. **修正字段映射**:
   ```python
   # 需要从两个表联合查询
   query = """
   SELECT 
       u.id as user_id,
       u.username,
       u.avatar,
       u.phone,
       u.goal,
       u.major,
       up.real_name,
       up.bio,
       up.total_study_hours,
       u.created_at,
       u.updated_at
   FROM "user" u
   LEFT JOIN user_profile up ON u.id = up.user_id
   WHERE u.id = :user_id
   """
   ```

3. **更新字段**:
   - `create_time` → `created_at`
   - `update_time` → `updated_at`
   - 移除不存在的字段: `nickname`, `email`, `is_public`, `allow_follow`

### 优先级2: Schema调整

修改 `UserProfileResponse` 以匹配实际数据库：

```python
# models/schemas/user.py
class UserProfileResponse(BaseModel):
    user_id: int
    username: str
    avatar: Optional[str]
    phone: str
    goal: Optional[str]
    major: Optional[str]
    real_name: Optional[str]  # 从user_profile表
    bio: Optional[str]  # 从user_profile表
    total_study_hours: Decimal = Decimal('0.0')  # 从user_profile表
    total_moments: int = 0
    total_badges: int = 0
    created_at: datetime
    updated_at: datetime
```

### 优先级3: 认证中间件

实现或配置 `get_current_user` 依赖：

```python
# core/dependencies.py
from fastapi import Depends, HTTPException, Header
from typing import Optional

async def get_current_user_dev(user_id: Optional[int] = None) -> dict:
    """开发环境模拟认证（通过query参数传递user_id）"""
    if not user_id:
        raise HTTPException(status_code=401, detail="未认证")
    return {"id": user_id}

# 或者实现真实的JWT认证
async def get_current_user(authorization: str = Header(None)) -> dict:
    """JWT认证（生产环境）"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证令牌")
    # 解析JWT token
    # ...
    return {"id": user_id}
```

---

## 📁 涉及文件清单

### 需要修改的文件
1. ❌ `backend/crud/user/crud_user_profile.py` - 修正表名和字段
2. ❌ `backend/models/schemas/user.py` - 调整UserProfileResponse
3. ❌ `backend/services/user/user_profile_service.py` - 适配新字段
4. ⚠️ `backend/core/dependencies.py` - 实现认证中间件

### 测试文件
- ✅ `backend/tests/test_user_profiles_apis.py` - 测试脚本已创建
- ✅ `backend/tests/USER_PROFILES_INITIAL_TEST.log` - 初始测试日志

---

## 💡 数据库设计说明

当前设计将用户信息分为两个表：

1. **`user` 表** - 核心用户信息
   - 用于认证和基本信息
   - 包含：用户名、手机、密码、头像、目标、专业等

2. **`user_profile` 表** - 扩展用户信息
   - 一对一关系（通过user_id）
   - 包含：真实姓名、简介、学习时长等

**优点**:
- 分离核心数据和扩展数据
- 提高查询效率
- 便于扩展

**建议**:
- 如果需要`nickname`、`email`等字段，应该添加到`user`表
- 如果需要`is_public`、`allow_follow`等字段，应该添加到`user_profile`表

---

## 🎯 下一步行动

1. **立即修复**:
   - [ ] 修复CRUD层的表名和字段引用
   - [ ] 调整Schema定义
   - [ ] 添加`text()`包装器到所有SQL查询

2. **后续完善**:
   - [ ] 实现认证中间件
   - [ ] 完善Moment和Badge服务集成
   - [ ] 添加数据验证

3. **测试验证**:
   - [ ] CRUD层单元测试
   - [ ] API端点集成测试
   - [ ] 数据库交互验证

---

## 📝 总结

**当前状态**:
- ✅ 数据库结构完整且设计合理
- ✅ 测试数据可以正常创建和清理
- ❌ CRUD层与数据库Schema不匹配
- ⚠️ API层缺少认证支持

**预估工作量**:
- CRUD层修复：1-2小时
- Schema调整：30分钟
- 认证中间件：1-2小时
- 测试验证：1小时

**总计**: 约4-6小时可以完全修复并测试通过

---

**报告生成时间**: 2025-10-02  
**分析人员**: AI Assistant  
**环境**: PostgreSQL 14 + FastAPI + SQLAlchemy 2.0 