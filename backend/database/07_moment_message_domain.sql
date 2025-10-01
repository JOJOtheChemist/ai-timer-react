-- ============================================================================
-- 六、动态与消息域（支撑动态广场、消息中心）
-- ============================================================================

-- 1. 动态表
CREATE TABLE moment (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL, -- 发布者
    type SMALLINT NOT NULL CHECK (type IN (0, 1, 2)), -- 0-动态，1-干货，2-系统广告
    title VARCHAR(200) DEFAULT NULL, -- 标题（干货必填，动态可空）
    content TEXT NOT NULL, -- 内容
    image_url VARCHAR(255) DEFAULT NULL, -- 图片URL
    tags JSONB DEFAULT '[]'::jsonb, -- 标签数组，如["#考研英语","#今日复盘"]
    like_count INTEGER DEFAULT 0 CHECK (like_count >= 0), -- 点赞数
    comment_count INTEGER DEFAULT 0 CHECK (comment_count >= 0), -- 评论数
    share_count INTEGER DEFAULT 0 CHECK (share_count >= 0), -- 分享数
    view_count INTEGER DEFAULT 0 CHECK (view_count >= 0), -- 查看数
    is_top SMALLINT DEFAULT 0 CHECK (is_top IN (0, 1)), -- 是否置顶（广告专用）
    ad_info VARCHAR(200) DEFAULT NULL, -- 广告信息（仅广告类型使用）
    status SMALLINT DEFAULT 0 CHECK (status IN (0, 1, 2)), -- 0-正常，1-隐藏，2-删除
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 2. 动态附件表
CREATE TABLE moment_attachment (
    id BIGSERIAL PRIMARY KEY,
    moment_id BIGINT NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('schedule', 'method', 'file', 'image')), -- 附件类型
    related_id BIGINT DEFAULT NULL, -- 关联ID（如时间表ID、方法ID）
    name VARCHAR(100) NOT NULL, -- 附件名
    file_url VARCHAR(255) DEFAULT NULL, -- 文件URL
    file_size INTEGER DEFAULT NULL, -- 文件大小（字节）
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (moment_id) REFERENCES moment(id) ON DELETE CASCADE
);

-- 3. 动态互动表
CREATE TABLE moment_interaction (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    moment_id BIGINT NOT NULL,
    interaction_type SMALLINT NOT NULL CHECK (interaction_type IN (0, 1, 2)), -- 0-点赞，1-收藏，2-分享
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (moment_id) REFERENCES moment(id) ON DELETE CASCADE,
    UNIQUE (user_id, moment_id, interaction_type) -- 避免重复互动
);

-- 4. 动态评论表
CREATE TABLE moment_comment (
    id BIGSERIAL PRIMARY KEY,
    moment_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL, -- 评论内容
    parent_id BIGINT DEFAULT NULL, -- 父评论ID，用于回复
    like_count INTEGER DEFAULT 0 CHECK (like_count >= 0), -- 评论点赞数
    is_anonymous SMALLINT DEFAULT 0 CHECK (is_anonymous IN (0, 1)), -- 是否匿名
    status SMALLINT DEFAULT 0 CHECK (status IN (0, 1, 2)), -- 0-正常，1-隐藏，2-删除
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (moment_id) REFERENCES moment(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES moment_comment(id) ON DELETE CASCADE
);

-- 5. 消息表
CREATE TABLE message (
    id BIGSERIAL PRIMARY KEY,
    sender_id BIGINT DEFAULT NULL, -- 发送者ID，系统消息为NULL
    receiver_id BIGINT NOT NULL, -- 接收者ID
    type SMALLINT NOT NULL CHECK (type IN (0, 1, 2)), -- 0-导师反馈，1-私信，2-系统通知
    title VARCHAR(100) DEFAULT NULL, -- 消息标题
    content TEXT NOT NULL, -- 消息内容
    is_unread SMALLINT DEFAULT 1 CHECK (is_unread IN (0, 1)), -- 是否未读
    related_id BIGINT DEFAULT NULL, -- 关联ID（如导师ID、时间表ID）
    related_type VARCHAR(20) DEFAULT NULL, -- 关联类型（tutor、schedule、order等）
    attachment_url VARCHAR(255) DEFAULT NULL, -- 附件URL
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_time TIMESTAMP WITH TIME ZONE DEFAULT NULL, -- 阅读时间
    FOREIGN KEY (sender_id) REFERENCES "user"(id) ON DELETE SET NULL,
    FOREIGN KEY (receiver_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 6. 消息回复表
CREATE TABLE message_reply (
    id BIGSERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL, -- 回复者
    content TEXT NOT NULL, -- 回复内容
    attachment_url VARCHAR(255) DEFAULT NULL, -- 附件URL
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES message(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 7. 消息模板表（用于系统通知）
CREATE TABLE message_template (
    id BIGSERIAL PRIMARY KEY,
    template_code VARCHAR(50) UNIQUE NOT NULL, -- 模板代码
    template_name VARCHAR(100) NOT NULL, -- 模板名称
    title_template VARCHAR(200) NOT NULL, -- 标题模板
    content_template TEXT NOT NULL, -- 内容模板
    type SMALLINT NOT NULL CHECK (type IN (0, 1, 2)), -- 消息类型
    is_active SMALLINT DEFAULT 1 CHECK (is_active IN (0, 1)), -- 是否启用
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_moment_user_id ON moment(user_id);
CREATE INDEX idx_moment_type ON moment(type);
CREATE INDEX idx_moment_status ON moment(status);
CREATE INDEX idx_moment_is_top ON moment(is_top);
CREATE INDEX idx_moment_like_count ON moment(like_count);
CREATE INDEX idx_moment_create_time ON moment(create_time);
CREATE INDEX idx_moment_view_count ON moment(view_count);

CREATE INDEX idx_moment_attachment_moment_id ON moment_attachment(moment_id);
CREATE INDEX idx_moment_attachment_type ON moment_attachment(type);
CREATE INDEX idx_moment_attachment_related_id ON moment_attachment(related_id);

CREATE INDEX idx_moment_interaction_user_id ON moment_interaction(user_id);
CREATE INDEX idx_moment_interaction_moment_id ON moment_interaction(moment_id);
CREATE INDEX idx_moment_interaction_type ON moment_interaction(interaction_type);
CREATE INDEX idx_moment_interaction_create_time ON moment_interaction(create_time);

CREATE INDEX idx_moment_comment_moment_id ON moment_comment(moment_id);
CREATE INDEX idx_moment_comment_user_id ON moment_comment(user_id);
CREATE INDEX idx_moment_comment_parent_id ON moment_comment(parent_id);
CREATE INDEX idx_moment_comment_status ON moment_comment(status);
CREATE INDEX idx_moment_comment_create_time ON moment_comment(create_time);

CREATE INDEX idx_message_sender_id ON message(sender_id);
CREATE INDEX idx_message_receiver_id ON message(receiver_id);
CREATE INDEX idx_message_type ON message(type);
CREATE INDEX idx_message_is_unread ON message(is_unread);
CREATE INDEX idx_message_related_id ON message(related_id);
CREATE INDEX idx_message_create_time ON message(create_time);
CREATE INDEX idx_message_receiver_unread ON message(receiver_id, is_unread);

CREATE INDEX idx_message_reply_message_id ON message_reply(message_id);
CREATE INDEX idx_message_reply_user_id ON message_reply(user_id);
CREATE INDEX idx_message_reply_create_time ON message_reply(create_time);

CREATE INDEX idx_message_template_code ON message_template(template_code);
CREATE INDEX idx_message_template_type ON message_template(type);
CREATE INDEX idx_message_template_is_active ON message_template(is_active);

-- 添加 GIN 索引支持 JSONB 标签查询
CREATE INDEX idx_moment_tags_gin ON moment USING GIN (tags);

-- 添加全文搜索索引
CREATE INDEX idx_moment_content_search ON moment USING GIN (to_tsvector('chinese', content));
CREATE INDEX idx_message_content_search ON message USING GIN (to_tsvector('chinese', content));

-- 为相关表添加更新时间触发器
CREATE TRIGGER update_moment_update_time BEFORE UPDATE ON moment 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_message_template_update_time BEFORE UPDATE ON message_template 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建函数用于更新动态统计信息
CREATE OR REPLACE FUNCTION update_moment_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- 更新动态的互动统计
    IF TG_OP IN ('INSERT', 'DELETE') AND TG_TABLE_NAME = 'moment_interaction' THEN
        UPDATE moment 
        SET 
            like_count = (
                SELECT COUNT(*) 
                FROM moment_interaction 
                WHERE moment_id = COALESCE(NEW.moment_id, OLD.moment_id) 
                AND interaction_type = 0
            ),
            share_count = (
                SELECT COUNT(*) 
                FROM moment_interaction 
                WHERE moment_id = COALESCE(NEW.moment_id, OLD.moment_id) 
                AND interaction_type = 2
            )
        WHERE id = COALESCE(NEW.moment_id, OLD.moment_id);
    END IF;
    
    -- 更新动态的评论数
    IF TG_OP IN ('INSERT', 'DELETE') AND TG_TABLE_NAME = 'moment_comment' THEN
        UPDATE moment 
        SET comment_count = (
            SELECT COUNT(*) 
            FROM moment_comment 
            WHERE moment_id = COALESCE(NEW.moment_id, OLD.moment_id) 
            AND status = 0
        )
        WHERE id = COALESCE(NEW.moment_id, OLD.moment_id);
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 创建触发器自动更新统计信息
CREATE TRIGGER trigger_update_moment_interaction_stats 
    AFTER INSERT OR DELETE ON moment_interaction
    FOR EACH ROW EXECUTE FUNCTION update_moment_stats();

CREATE TRIGGER trigger_update_moment_comment_stats 
    AFTER INSERT OR DELETE ON moment_comment
    FOR EACH ROW EXECUTE FUNCTION update_moment_stats();

-- 创建函数用于自动标记消息为已读
CREATE OR REPLACE FUNCTION mark_message_as_read()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_unread = 0 AND OLD.is_unread = 1 THEN
        NEW.read_time = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器自动设置消息阅读时间
CREATE TRIGGER trigger_mark_message_read 
    BEFORE UPDATE ON message
    FOR EACH ROW EXECUTE FUNCTION mark_message_as_read();

-- 添加表注释
COMMENT ON TABLE moment IS '动态表';
COMMENT ON TABLE moment_attachment IS '动态附件表';
COMMENT ON TABLE moment_interaction IS '动态互动表';
COMMENT ON TABLE moment_comment IS '动态评论表';
COMMENT ON TABLE message IS '消息表';
COMMENT ON TABLE message_reply IS '消息回复表';
COMMENT ON TABLE message_template IS '消息模板表';

-- 添加字段注释
COMMENT ON COLUMN moment.type IS '动态类型：0-动态，1-干货，2-系统广告';
COMMENT ON COLUMN moment.tags IS '标签数组，JSON格式';
COMMENT ON COLUMN moment.is_top IS '是否置顶：0-否，1-是（广告专用）';
COMMENT ON COLUMN moment.status IS '状态：0-正常，1-隐藏，2-删除';

COMMENT ON COLUMN moment_attachment.type IS '附件类型：schedule-时间表，method-学习方法，file-文件，image-图片';
COMMENT ON COLUMN moment_attachment.related_id IS '关联ID（如时间表ID、方法ID）';

COMMENT ON COLUMN moment_interaction.interaction_type IS '互动类型：0-点赞，1-收藏，2-分享';

COMMENT ON COLUMN moment_comment.parent_id IS '父评论ID，用于回复功能';
COMMENT ON COLUMN moment_comment.is_anonymous IS '是否匿名评论：0-否，1-是';
COMMENT ON COLUMN moment_comment.status IS '评论状态：0-正常，1-隐藏，2-删除';

COMMENT ON COLUMN message.type IS '消息类型：0-导师反馈，1-私信，2-系统通知';
COMMENT ON COLUMN message.is_unread IS '是否未读：0-已读，1-未读';
COMMENT ON COLUMN message.related_type IS '关联类型：tutor-导师，schedule-时间表，order-订单等';

COMMENT ON COLUMN message_template.template_code IS '模板代码，如BADGE_OBTAINED';
COMMENT ON COLUMN message_template.title_template IS '标题模板，支持变量替换';
COMMENT ON COLUMN message_template.content_template IS '内容模板，支持变量替换';

-- 创建复合索引优化常用查询
CREATE INDEX idx_moment_type_status_time ON moment(type, status, create_time DESC);
CREATE INDEX idx_moment_user_status_time ON moment(user_id, status, create_time DESC);
CREATE INDEX idx_message_receiver_type_unread ON message(receiver_id, type, is_unread);
CREATE INDEX idx_moment_comment_moment_parent_time ON moment_comment(moment_id, parent_id, create_time DESC);

-- 创建视图：热门动态
CREATE VIEW v_hot_moments AS
SELECT 
    m.*,
    u.username,
    u.avatar,
    CASE 
        WHEN m.like_count >= 100 THEN '热门'
        WHEN m.like_count >= 50 THEN '推荐'
        ELSE '普通'
    END as popularity_level,
    (m.like_count * 2 + m.comment_count * 3 + m.share_count * 5) as engagement_score
FROM moment m
JOIN "user" u ON m.user_id = u.id
WHERE m.status = 0
ORDER BY engagement_score DESC, m.create_time DESC;

-- 创建视图：用户未读消息统计
CREATE VIEW v_user_unread_messages AS
SELECT 
    receiver_id as user_id,
    COUNT(*) as total_unread,
    COUNT(CASE WHEN type = 0 THEN 1 END) as tutor_unread,
    COUNT(CASE WHEN type = 1 THEN 1 END) as private_unread,
    COUNT(CASE WHEN type = 2 THEN 1 END) as system_unread
FROM message
WHERE is_unread = 1
GROUP BY receiver_id; 