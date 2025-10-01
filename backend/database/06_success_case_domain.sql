-- ============================================================================
-- 五、成功案例域（支撑成功案例页）
-- ============================================================================

-- 1. 成功案例表
CREATE TABLE success_case (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL, -- 案例作者
    title VARCHAR(200) NOT NULL, -- 案例标题
    icon VARCHAR(20) DEFAULT '📚', -- 图标
    duration VARCHAR(20) NOT NULL, -- 投入时长，如"976h"
    tags JSONB DEFAULT '[]'::jsonb, -- 标签数组，如["高考","失恋逆袭","日均13h"]
    author_name VARCHAR(50) NOT NULL, -- 上岸者名
    view_count INTEGER DEFAULT 0 CHECK (view_count >= 0), -- 查看人数
    like_count INTEGER DEFAULT 0 CHECK (like_count >= 0), -- 点赞数
    collect_count INTEGER DEFAULT 0 CHECK (collect_count >= 0), -- 收藏数
    is_hot SMALLINT DEFAULT 0 CHECK (is_hot IN (0, 1)), -- 是否热门
    preview_days INTEGER DEFAULT 3 CHECK (preview_days >= 0), -- 免费预览天数
    price VARCHAR(20) DEFAULT NULL, -- 查看价格，如"88钻石查看"
    content TEXT NOT NULL, -- 案例详细内容
    summary TEXT DEFAULT NULL, -- 案例摘要
    difficulty_level SMALLINT DEFAULT 1 CHECK (difficulty_level BETWEEN 1 AND 5), -- 难度等级1-5
    category VARCHAR(50) DEFAULT NULL, -- 案例分类，如"考研"、"高考"、"技能提升"
    status SMALLINT DEFAULT 0 CHECK (status IN (0, 1, 2)), -- 0-待审核，1-已发布，2-已下架
    admin_review_note TEXT DEFAULT NULL, -- 管理员审核备注
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    publish_time TIMESTAMP WITH TIME ZONE DEFAULT NULL, -- 发布时间
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 2. 案例互动表（点赞、收藏）
CREATE TABLE case_interaction (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    case_id BIGINT NOT NULL,
    interaction_type SMALLINT NOT NULL CHECK (interaction_type IN (0, 1)), -- 0-点赞，1-收藏
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (case_id) REFERENCES success_case(id) ON DELETE CASCADE,
    UNIQUE (user_id, case_id, interaction_type) -- 避免重复互动
);

-- 3. 案例评论表
CREATE TABLE case_comment (
    id BIGSERIAL PRIMARY KEY,
    case_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL, -- 评论内容
    parent_id BIGINT DEFAULT NULL, -- 父评论ID，用于回复
    like_count INTEGER DEFAULT 0 CHECK (like_count >= 0), -- 评论点赞数
    is_anonymous SMALLINT DEFAULT 0 CHECK (is_anonymous IN (0, 1)), -- 是否匿名
    status SMALLINT DEFAULT 0 CHECK (status IN (0, 1, 2)), -- 0-正常，1-隐藏，2-删除
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES success_case(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES case_comment(id) ON DELETE CASCADE
);

-- 4. 案例购买记录表
CREATE TABLE case_purchase (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    case_id BIGINT NOT NULL,
    amount INTEGER NOT NULL CHECK (amount >= 0), -- 购买金额（钻石）
    purchase_type SMALLINT DEFAULT 0 CHECK (purchase_type IN (0, 1)), -- 0-钻石购买，1-免费获取
    expire_time TIMESTAMP WITH TIME ZONE DEFAULT NULL, -- 过期时间（如果有限制）
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (case_id) REFERENCES success_case(id) ON DELETE CASCADE,
    UNIQUE (user_id, case_id) -- 每个用户每个案例只能购买一次
);

-- 5. 案例标签表（预定义标签）
CREATE TABLE case_tag (
    id BIGSERIAL PRIMARY KEY,
    tag_name VARCHAR(50) UNIQUE NOT NULL, -- 标签名
    tag_category VARCHAR(20) DEFAULT 'general', -- 标签分类
    use_count INTEGER DEFAULT 0 CHECK (use_count >= 0), -- 使用次数
    is_active SMALLINT DEFAULT 1 CHECK (is_active IN (0, 1)), -- 是否启用
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_success_case_user_id ON success_case(user_id);
CREATE INDEX idx_success_case_status ON success_case(status);
CREATE INDEX idx_success_case_is_hot ON success_case(is_hot);
CREATE INDEX idx_success_case_view_count ON success_case(view_count);
CREATE INDEX idx_success_case_like_count ON success_case(like_count);
CREATE INDEX idx_success_case_category ON success_case(category);
CREATE INDEX idx_success_case_difficulty_level ON success_case(difficulty_level);
CREATE INDEX idx_success_case_create_time ON success_case(create_time);
CREATE INDEX idx_success_case_publish_time ON success_case(publish_time);

CREATE INDEX idx_case_interaction_user_id ON case_interaction(user_id);
CREATE INDEX idx_case_interaction_case_id ON case_interaction(case_id);
CREATE INDEX idx_case_interaction_type ON case_interaction(interaction_type);
CREATE INDEX idx_case_interaction_create_time ON case_interaction(create_time);

CREATE INDEX idx_case_comment_case_id ON case_comment(case_id);
CREATE INDEX idx_case_comment_user_id ON case_comment(user_id);
CREATE INDEX idx_case_comment_parent_id ON case_comment(parent_id);
CREATE INDEX idx_case_comment_status ON case_comment(status);
CREATE INDEX idx_case_comment_create_time ON case_comment(create_time);

CREATE INDEX idx_case_purchase_user_id ON case_purchase(user_id);
CREATE INDEX idx_case_purchase_case_id ON case_purchase(case_id);
CREATE INDEX idx_case_purchase_create_time ON case_purchase(create_time);

CREATE INDEX idx_case_tag_tag_name ON case_tag(tag_name);
CREATE INDEX idx_case_tag_category ON case_tag(tag_category);
CREATE INDEX idx_case_tag_use_count ON case_tag(use_count);
CREATE INDEX idx_case_tag_is_active ON case_tag(is_active);

-- 添加 GIN 索引支持 JSONB 标签查询
CREATE INDEX idx_success_case_tags_gin ON success_case USING GIN (tags);

-- 为相关表添加更新时间触发器
CREATE TRIGGER update_success_case_update_time BEFORE UPDATE ON success_case 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建函数用于更新案例统计信息
CREATE OR REPLACE FUNCTION update_case_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- 更新案例的点赞数和收藏数
    IF TG_OP IN ('INSERT', 'DELETE') AND TG_TABLE_NAME = 'case_interaction' THEN
        UPDATE success_case 
        SET 
            like_count = (
                SELECT COUNT(*) 
                FROM case_interaction 
                WHERE case_id = COALESCE(NEW.case_id, OLD.case_id) 
                AND interaction_type = 0
            ),
            collect_count = (
                SELECT COUNT(*) 
                FROM case_interaction 
                WHERE case_id = COALESCE(NEW.case_id, OLD.case_id) 
                AND interaction_type = 1
            )
        WHERE id = COALESCE(NEW.case_id, OLD.case_id);
    END IF;
    
    -- 更新案例查看数（通过购买记录）
    IF TG_OP = 'INSERT' AND TG_TABLE_NAME = 'case_purchase' THEN
        UPDATE success_case 
        SET view_count = view_count + 1
        WHERE id = NEW.case_id;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 创建触发器自动更新统计信息
CREATE TRIGGER trigger_update_case_interaction_stats 
    AFTER INSERT OR DELETE ON case_interaction
    FOR EACH ROW EXECUTE FUNCTION update_case_stats();

CREATE TRIGGER trigger_update_case_view_stats 
    AFTER INSERT ON case_purchase
    FOR EACH ROW EXECUTE FUNCTION update_case_stats();

-- 添加表注释
COMMENT ON TABLE success_case IS '成功案例表';
COMMENT ON TABLE case_interaction IS '案例互动表（点赞、收藏）';
COMMENT ON TABLE case_comment IS '案例评论表';
COMMENT ON TABLE case_purchase IS '案例购买记录表';
COMMENT ON TABLE case_tag IS '案例标签表';

-- 添加字段注释
COMMENT ON COLUMN success_case.duration IS '投入时长，如"976h"';
COMMENT ON COLUMN success_case.tags IS '标签数组，JSON格式';
COMMENT ON COLUMN success_case.is_hot IS '是否热门：0-否，1-是';
COMMENT ON COLUMN success_case.preview_days IS '免费预览天数';
COMMENT ON COLUMN success_case.difficulty_level IS '难度等级：1-5';
COMMENT ON COLUMN success_case.status IS '状态：0-待审核，1-已发布，2-已下架';

COMMENT ON COLUMN case_interaction.interaction_type IS '互动类型：0-点赞，1-收藏';

COMMENT ON COLUMN case_comment.parent_id IS '父评论ID，用于回复功能';
COMMENT ON COLUMN case_comment.is_anonymous IS '是否匿名评论：0-否，1-是';
COMMENT ON COLUMN case_comment.status IS '评论状态：0-正常，1-隐藏，2-删除';

COMMENT ON COLUMN case_purchase.purchase_type IS '购买类型：0-钻石购买，1-免费获取';
COMMENT ON COLUMN case_purchase.amount IS '购买金额（钻石）';

COMMENT ON COLUMN case_tag.tag_category IS '标签分类';
COMMENT ON COLUMN case_tag.use_count IS '标签使用次数';

-- 创建复合索引优化常用查询
CREATE INDEX idx_success_case_status_hot_view ON success_case(status, is_hot, view_count DESC);
CREATE INDEX idx_success_case_category_status_time ON success_case(category, status, create_time DESC);
CREATE INDEX idx_case_comment_case_parent_time ON case_comment(case_id, parent_id, create_time DESC);

-- 创建视图：热门案例
CREATE VIEW v_hot_success_cases AS
SELECT 
    sc.*,
    CASE 
        WHEN sc.view_count >= 1000 THEN '超热门'
        WHEN sc.view_count >= 500 THEN '热门'
        WHEN sc.view_count >= 100 THEN '推荐'
        ELSE '普通'
    END as popularity_level,
    (sc.like_count + sc.collect_count * 2) as engagement_score -- 参与度评分
FROM success_case sc
WHERE sc.status = 1
ORDER BY engagement_score DESC, sc.view_count DESC;

-- 创建视图：案例统计概览
CREATE VIEW v_case_stats_overview AS
SELECT 
    sc.id,
    sc.title,
    sc.author_name,
    sc.view_count,
    sc.like_count,
    sc.collect_count,
    COUNT(cc.id) as comment_count,
    COUNT(cp.id) as purchase_count
FROM success_case sc
LEFT JOIN case_comment cc ON sc.id = cc.case_id AND cc.status = 0
LEFT JOIN case_purchase cp ON sc.id = cp.case_id
WHERE sc.status = 1
GROUP BY sc.id, sc.title, sc.author_name, sc.view_count, sc.like_count, sc.collect_count
ORDER BY sc.view_count DESC; 