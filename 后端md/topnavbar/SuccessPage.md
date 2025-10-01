# 成功案例页（SuccessPage）业务域-文件映射表

| 成功案例页核心功能                        | 对应业务域 | 后端文件路径                              | 核心函数/接口说明                                                                   |
| ----------------------------------------- | ---------- | ----------------------------------------- | ----------------------------------------------------------------------------------- |
| 1. 热门推荐案例展示（含热门标签、浏览量） | case       | api/v1/endpoints/case/cases.py            | - GET /api/v1/cases/hot：获取热门推荐案例（按浏览量/热度排序）                      |
|                                           | case       | services/case/case_service.py             | - get_hot_cases(limit=3)：查询热门案例（默认取前3条，带isHot标记）                  |
|                                           | case       | crud/case/crud_case.py                    | - get_hot_by_views(db, limit)：按浏览量倒序查询热门案例                             |
|                                           | case       | models/schemas/case.py                    | - HotCaseResponse：热门案例响应模型（含id、title、tags、author、views、isHot等）    |
| 2. 案例列表展示（含筛选结果）             | case       | api/v1/endpoints/case/cases.py            | - GET /api/v1/cases：获取案例列表（支持筛选参数：category、duration等）             |
|                                           | case       | services/case/case_service.py             | - get_filtered_cases(filters)：根据筛选条件（分类、时长等）查询案例列表             |
|                                           | case       | crud/case/crud_case.py                    | - get_multi_by_filters(db, filters)：按筛选条件从数据库查询案例                     |
|                                           | case       | models/schemas/case.py                    | - CaseListResponse：案例列表响应模型（含id、title、tags、duration、price等）        |
| 3. 筛选功能（分类、时长、经历、基础）     | case       | api/v1/endpoints/case/cases.py            | - 复用GET /api/v1/cases接口，通过query参数传递筛选条件（category、duration等）      |
|                                           | case       | services/case/case_service.py             | - parse_filters(filter_params)：解析前端筛选参数，转换为数据库查询条件              |
|                                           | case       | models/schemas/case.py                    | - CaseFilterParams：筛选参数请求模型（定义category、duration等可选参数）            |
| 4. 搜索功能（按目标/时长/经历搜索）       | case       | api/v1/endpoints/case/cases.py            | - GET /api/v1/cases/search：按关键词搜索案例（支持title、tags、author等字段匹配）   |
|                                           | case       | services/case/case_service.py             | - search_cases(keyword)：根据关键词搜索案例（多字段模糊匹配）                       |
|                                           | case       | crud/case/crud_case.py                    | - search_by_keyword(db, keyword)：执行数据库模糊查询，匹配案例相关字段              |
| 5. 查看案例详情                           | case       | api/v1/endpoints/case/case_details.py     | - GET /api/v1/cases/{case_id}：获取单个案例的详细信息                               |
|                                           | case       | services/case/case_detail_service.py      | - get_case_detail(case_id)：查询案例详情（含完整描述、时间规划、经验总结等）        |
|                                           | case       | crud/case/crud_case_detail.py             | - get_by_id(db, case_id)：查询案例详情数据                                          |
|                                           | case       | models/schemas/case.py                    | - CaseDetailResponse：案例详情响应模型（含完整字段，如详细描述、时间规划表等）      |
| 6. 案例作者信息展示（上岸者名称）         | user       | api/v1/endpoints/user/user_profiles.py    | - GET /api/v1/users/{user_id}/simple-info：获取用户简易信息（仅名称，保护隐私）     |
|                                           | user       | services/user/user_profile_service.py     | - get_simple_user_info(user_id)：查询用户公开的简易信息（仅名称、头像等非敏感信息） |
|                                           | user       | crud/user/crud_user_profile.py            | - get_simple_info(db, user_id)：从数据库查询用户简易信息                            |
|                                           | user       | models/schemas/user.py                    | - UserSimpleInfoResponse：用户简易信息响应模型（含id、username、avatar等）          |
| 7. 案例预览/价格信息展示                  | case       | api/v1/endpoints/case/case_permissions.py | - GET /api/v1/cases/{case_id}/permission：获取案例的预览权限和价格信息              |
|                                           | case       | services/case/case_permission_service.py  | - get_case_permission(case_id, user_id)：查询案例的预览范围和查看价格               |
|                                           | case       | crud/case/crud_case_permission.py         | - get_permission_info(db, case_id)：查询案例的权限配置（预览天数、价格等）          |
|                                           | case       | models/schemas/case.py                    | - CasePermissionResponse：案例权限响应模型（含preview_days、price、currency等）     |

### 说明

1. 核心业务域为 `case`（案例），所有案例相关功能（展示、筛选、搜索、详情）均围绕该业务域展开，确保代码内聚；
2. 作者信息展示依赖 `user`业务域，但仅获取“非敏感简易信息”（名称、头像），通过专门的 `/users/{user_id}/simple-info`接口实现，避免暴露用户隐私数据；
3. 筛选和搜索功能通过“接口参数复用+服务层解析”实现，无需单独创建接口，简化前端调用逻辑；
4. 案例的权限和价格信息独立为 `case_permissions`模块，为后续扩展“付费查看”“权限管理”预留扩展空间。

如需继续分析下一个页面，直接提供对应的React文件即可～
