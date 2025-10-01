# 消息中心页（MessagePage）业务域-文件映射表

| 消息中心页核心功能                                  | 对应业务域 | 后端文件路径                                     | 核心函数/接口说明                                                                                                                                                          |
| --------------------------------------------------- | ---------- | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. 消息列表展示（分标签页：导师反馈/私信/系统通知） | message    | api/v1/endpoints/message/messages.py             | - GET /api/v1/messages：获取消息列表（支持type参数：tutor/private/system，默认tutor）`<br>`- 自动区分未读/已读状态，返回未读消息数用于徽章显示                           |
|                                                     | message    | services/message/message_service.py              | - get_message_list(user_id, message_type, page, page_size)：按类型查询用户消息列表，包含未读标记`<br>`- 为不同类型消息补充关联信息（如导师认证状态、发送方基础信息）     |
|                                                     | message    | crud/message/crud_message.py                     | - get_multi_by_type(db, user_id, message_type, page, page_size)：按类型从数据库查询消息`<br>`- count_unread_by_type(db, user_id, message_type)：统计指定类型的未读消息数 |
|                                                     | message    | models/schemas/message.py                        | - MessageListResponse：消息列表响应模型（含id、sender、content、time、is_unread等）`<br>`- MessageTypeEnum：枚举消息类型（tutor/private/system）                         |
| 2. 消息详情查看（导师反馈历史/完整内容）            | message    | api/v1/endpoints/message/message_details.py      | - GET /api/v1/messages/{message_id}：获取单条消息详情（含完整内容、关联上下文，如导师反馈的历史记录）                                                                      |
|                                                     | message    | services/message/message_detail_service.py       | - get_message_detail(user_id, message_id)：查询消息详情，验证消息归属（确保用户只能查看自己的消息）`<br>`- 对导师反馈类型，额外关联查询历史互动记录                      |
|                                                     | message    | crud/message/crud_message_detail.py              | - get_by_id_with_context(db, user_id, message_id)：查询消息详情及关联上下文（如同一导师的历史反馈）                                                                        |
|                                                     | message    | models/schemas/message.py                        | - MessageDetailResponse：消息详情响应模型（含完整content、context历史列表、关联资源ID等）                                                                                  |
| 3. 消息互动（回复导师/查看私信/查看关联内容）       | message    | api/v1/endpoints/message/message_interactions.py | - POST /api/v1/messages/{message_id}/reply：回复消息（支持对导师反馈/私信的回复，自动关联原消息）`<br>`- POST /api/v1/messages/{message_id}/mark-read：标记消息为已读    |
|                                                     | message    | services/message/message_interaction_service.py  | - reply_to_message(user_id, message_id, content)：回复消息（自动填充接收方、关联原消息ID）`<br>`- mark_as_read(user_id, message_id)：标记消息为已读（更新is_unread状态） |
|                                                     | message    | crud/message/crud_message_interaction.py         | - create_reply(db, user_id, message_id, content)：创建回复消息（作为新消息记录，关联原消息）`<br>`- update_read_status(db, user_id, message_id)：更新消息的已读状态      |
|                                                     | message    | models/schemas/message.py                        | - MessageReplyCreate：回复消息请求模型（含content字段）`<br>`- InteractionResponse：互动操作响应模型（含更新后的消息状态）                                               |
| 4. 未读消息计数（标签页徽章）                       | message    | api/v1/endpoints/message/message_stats.py        | - GET /api/v1/messages/unread-stats：获取各类型消息的未读数量（用于标签页徽章显示）                                                                                        |
|                                                     | message    | services/message/message_stat_service.py         | - calculate_unread_stats(user_id)：统计用户所有类型消息的未读数量（tutor/private/system）                                                                                  |
|                                                     | message    | crud/message/crud_message_stat.py                | - count_unread_by_all_types(db, user_id)：按类型统计未读消息数量，返回汇总结果                                                                                             |
|                                                     | message    | models/schemas/message.py                        | - UnreadStatsResponse：未读统计响应模型（含tutor_count、private_count、system_count）                                                                                      |
| 5. 消息设置（提醒方式/清理等）                      | user       | api/v1/endpoints/user/user_message_settings.py   | - GET /api/v1/users/me/message-settings：获取用户消息设置（提醒方式、保留时长等）`<br>`- PUT /api/v1/users/me/message-settings：更新用户消息设置                         |
|                                                     | user       | services/user/user_message_setting_service.py    | - get_message_settings(user_id)：查询用户的消息偏好设置`<br>`- update_message_settings(user_id, setting_data)：更新消息设置（如提醒方式、自动清理天数）                  |
|                                                     | user       | crud/user/crud_user_message_setting.py           | - get_by_user_id(db, user_id)：查询用户的消息设置数据`<br>`- update(db, user_id, setting_data)：更新数据库中的消息设置                                                   |
|                                                     | user       | models/schemas/user.py                           | - MessageSettingResponse：消息设置响应模型（含reminder_type、keep_days等）`<br>`- MessageSettingUpdate：消息设置更新请求模型（定义可修改的设置字段）                     |

### 说明

1. **业务域划分逻辑**：所有消息展示、互动功能归为 `message`业务域（核心是消息数据的CRUD和状态管理）；消息设置属于用户个性化配置，归为 `user`业务域，与用户基础信息形成统一的用户配置体系。
2. **消息类型处理**：通过 `message_type`字段区分“导师反馈/私信/系统通知”，在 `service`层统一处理不同类型的特殊逻辑（如导师反馈关联导师认证状态、系统通知无需回复功能），避免为每种类型创建独立接口。
3. **未读状态管理**：所有消息默认标记为未读，查看详情或手动标记时更新状态，通过 `crud`层的 `update_read_status`统一处理，确保未读计数准确（与标签页徽章同步）。
4. **关联资源处理**：消息中提到的“时间表”“私信”等关联内容，`message`服务仅存储关联ID（如 `schedule_id`），前端跳转时需单独调用对应业务域的接口（如 `schedule`的详情接口），`message`服务不处理跨域资源的具体内容。

如果需要继续分析下一个页面，直接提供对应的React文件即可～
