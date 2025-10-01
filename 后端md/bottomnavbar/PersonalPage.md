# 个人主页（PersonalPage）业务域-文件映射表

| 个人主页核心功能                              | 对应业务域 | 后端文件路径                            | 核心函数/接口说明                                                                               |
| --------------------------------------------- | ---------- | --------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 1. 个人信息展示（头像、名称、目标、总时长等） | user       | api/v1/endpoints/user/user_profiles.py  | - GET /api/v1/users/me/profile：获取当前登录用户的完整个人信息（含基础信息、总学习时长）        |
|                                               | user       | services/user/user_profile_service.py   | - get_current_user_profile(user_id)：查询当前用户的个人信息（关联学习时长统计）                 |
|                                               | user       | crud/user/crud_user_profile.py          | - get_by_user_id(db, user_id)：从数据库查询用户个人信息                                         |
|                                               | user       | models/schemas/user.py                  | - UserProfileResponse：用户个人信息响应模型（含avatar、username、goal、total_hours等）          |
| 2. 个人信息编辑（打开编辑页面/提交修改）      | user       | api/v1/endpoints/user/user_profiles.py  | - PUT /api/v1/users/me/profile：更新当前用户的个人信息（如修改goal、username）                  |
|                                               | user       | services/user/user_profile_service.py   | - update_user_profile(user_id, profile_data)：更新用户个人信息（校验数据合法性）                |
|                                               | user       | crud/user/crud_user_profile.py          | - update(db, user_id, profile_data)：更新数据库中的用户个人信息                                 |
|                                               | user       | models/schemas/user.py                  | - UserProfileUpdate：用户信息更新请求模型（定义可修改的字段：goal、username等）                 |
| 3. 资产（钻石）展示与充值                     | user       | api/v1/endpoints/user/user_assets.py    | - GET /api/v1/users/me/assets：获取当前用户的资产信息（钻石数量、消费记录）                     |
|                                               | user       | api/v1/endpoints/user/user_assets.py    | - POST /api/v1/users/me/assets/recharge：发起钻石充值请求（生成充值订单/对接支付）              |
|                                               | user       | services/user/user_asset_service.py     | - get_user_assets(user_id)：查询用户资产及最近消费记录                                          |
|                                               | user       | services/user/user_asset_service.py     | - create_recharge_order(user_id, amount)：创建钻石充值订单（返回支付链接/订单号）               |
|                                               | user       | crud/user/crud_user_asset.py            | - get_asset_by_user_id(db, user_id)：查询用户资产数据                                           |
|                                               | user       | crud/user/crud_user_asset.py            | - get_recent_consume(db, user_id, limit=1)：查询用户最近1条消费记录                             |
|                                               | user       | models/schemas/user.py                  | - UserAssetResponse：用户资产响应模型（含diamond_count、recent_consume等）                      |
| 4. 关系链管理（关注导师/粉丝统计与列表）      | user       | api/v1/endpoints/user/user_relations.py | - GET /api/v1/users/me/relations/stats：获取用户关系统计（关注导师数、粉丝数）                  |
|                                               | user       | api/v1/endpoints/user/user_relations.py | - GET /api/v1/users/me/relations/tutors：获取用户关注的导师列表（紧凑版，默认前3条）            |
|                                               | user       | api/v1/endpoints/user/user_relations.py | - GET /api/v1/users/me/relations/fans：获取用户的最近粉丝列表（紧凑版，默认前4条）              |
|                                               | user       | services/user/user_relation_service.py  | - get_relation_stats(user_id)：统计用户的关注导师数、粉丝数                                     |
|                                               | user       | services/user/user_relation_service.py  | - get_followed_tutors(user_id, limit=3)：查询用户关注的导师列表（限制条数）                     |
|                                               | user       | services/user/user_relation_service.py  | - get_recent_fans(user_id, limit=4)：查询用户的最近粉丝列表（限制条数）                         |
|                                               | user       | crud/user/crud_user_relation.py         | - count_relations(db, user_id, relation_type)：统计指定类型的关系数量（导师/粉丝）              |
|                                               | user       | crud/user/crud_user_relation.py         | - get_followed_by_type(db, user_id, type, limit)：查询指定类型的关系列表                        |
|                                               | user       | models/schemas/user.py                  | - RelationStatsResponse：关系统计响应模型（含tutor_count、fan_count等）                         |
| 5. 徽章墙（展示、详情、解锁状态）             | badge      | api/v1/endpoints/badge/badges.py        | - GET /api/v1/badges/my：获取当前用户的徽章列表（含已获得/未解锁状态）                          |
|                                               | badge      | api/v1/endpoints/badge/badges.py        | - GET /api/v1/badges/{badge_id}：获取单个徽章的详情（描述、获得时间/解锁条件）                  |
|                                               | badge      | services/badge/badge_service.py         | - get_user_badges(user_id)：查询用户的所有徽章（关联解锁状态和获得时间）                        |
|                                               | badge      | services/badge/badge_service.py         | - get_badge_detail(badge_id, user_id)：查询徽章详情（含用户是否已获得）                         |
|                                               | badge      | crud/badge/crud_badge.py                | - get_user_badge_relations(db, user_id)：查询用户与徽章的关联数据（获得时间等）                 |
|                                               | badge      | crud/badge/crud_badge.py                | - get_by_id(db, badge_id)：查询徽章的基础信息（名称、描述、图标）                               |
|                                               | badge      | models/schemas/badge.py                 | - UserBadgeResponse：用户徽章列表响应模型（含badge_id、name、icon、is_obtained、obtain_date等） |
|                                               | badge      | models/schemas/badge.py                 | - BadgeDetailResponse：徽章详情响应模型（含desc、obtain_date/lock_condition等）                 |

### 说明

1. **业务域划分核心**：个人信息、资产、关系链归为 `user`业务域（均为用户核心关联数据），徽章归为独立 `badge`业务域（徽章有独立规则和数据结构，可复用至其他页面）；
2. **接口设计注意**：所有接口均用 `/api/v1/users/me/`前缀（表示“当前登录用户的资源”），避免暴露其他用户ID，保护隐私；
3. **关联数据处理**：用户总学习时长、资产消费记录等“关联数据”，通过 `service`层调用其他业务域接口（如总学习时长调用 `statistic_service`），不直接在 `user`的 `crud`层混杂其他业务逻辑；
4. **跳转类功能**：“功能入口跳转（时间表、动态）”是前端路由跳转，后端无需单独开发接口，只需确保目标页面的接口正常即可。

如果需要继续分析下一个页面，直接提供对应的React文件即可～
