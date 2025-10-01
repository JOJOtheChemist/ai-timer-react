-- ============================================================================
-- 三、学习方法与打卡域（支撑学习方法页）
-- ============================================================================

-- 1. 学习方法表
CREATE TABLE study_method (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(20) NOT NULL CHECK (category IN ('common', 'tutor')), -- common-通用方法，tutor-导师独创
    type VARCHAR(20) DEFAULT NULL, -- 适用类型，如"全学科""文科背诵"
    description TEXT NOT NULL,
    steps JSONB NOT NULL, -- 存储步骤数组，如["步骤1...","步骤2..."]
    scene VARCHAR(200) DEFAULT NULL, -- 推荐场景
    tutor_id BIGINT DEFAULT NULL, -- 导师独创方法时关联导师ID
    checkin_count INTEGER DEFAULT 0 CHECK (checkin_count >= 0), -- 总打卡人数
    rating DECIMAL(2,1) DEFAULT 0.0 CHECK (rating >= 0 AND rating <= 5.0), -- 评分
    review_count INTEGER DEFAULT 0 CHECK (review_count >= 0), -- 评价数
    status SMALLINT DEFAULT 0 CHECK (status IN (0, 1)), -- 0-启用，1-下架
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. 打卡记录表
CREATE TABLE checkin_record (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    method_id BIGINT NOT NULL,
    checkin_type VARCHAR(20) NOT NULL CHECK (checkin_type IN ('正字打卡', '计数打卡', '时长打卡')),
    progress INTEGER DEFAULT 1 CHECK (progress >= 1), -- 进度，如1-4遍
    note TEXT DEFAULT NULL, -- 打卡心得
    checkin_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (method_id) REFERENCES study_method(id) ON DELETE CASCADE,
    -- 单日同一方法仅可打卡1次
    UNIQUE (user_id, method_id, DATE(checkin_time AT TIME ZONE 'Asia/Shanghai'))
);

-- 3. 学习方法评价表
CREATE TABLE method_review (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    method_id BIGINT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5), -- 1-5星评分
    content TEXT DEFAULT NULL, -- 评价内容
    is_anonymous SMALLINT DEFAULT 0 CHECK (is_anonymous IN (0, 1)), -- 是否匿名评价
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (method_id) REFERENCES study_method(id) ON DELETE CASCADE,
    -- 每个用户对每个方法只能评价一次
    UNIQUE (user_id, method_id)
);

-- 创建索引
CREATE INDEX idx_study_method_category ON study_method(category);
CREATE INDEX idx_study_method_type ON study_method(type);
CREATE INDEX idx_study_method_tutor_id ON study_method(tutor_id);
CREATE INDEX idx_study_method_status ON study_method(status);
CREATE INDEX idx_study_method_rating ON study_method(rating);
CREATE INDEX idx_study_method_checkin_count ON study_method(checkin_count);
CREATE INDEX idx_study_method_create_time ON study_method(create_time);

CREATE INDEX idx_checkin_record_user_id ON checkin_record(user_id);
CREATE INDEX idx_checkin_record_method_id ON checkin_record(method_id);
CREATE INDEX idx_checkin_record_checkin_type ON checkin_record(checkin_type);
CREATE INDEX idx_checkin_record_checkin_time ON checkin_record(checkin_time);
CREATE INDEX idx_checkin_record_user_method ON checkin_record(user_id, method_id);

CREATE INDEX idx_method_review_user_id ON method_review(user_id);
CREATE INDEX idx_method_review_method_id ON method_review(method_id);
CREATE INDEX idx_method_review_rating ON method_review(rating);
CREATE INDEX idx_method_review_create_time ON method_review(create_time);

-- 为相关表添加更新时间触发器
CREATE TRIGGER update_study_method_update_time BEFORE UPDATE ON study_method 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建函数用于更新学习方法的统计信息
CREATE OR REPLACE FUNCTION update_method_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- 更新打卡人数
    IF TG_OP = 'INSERT' AND TG_TABLE_NAME = 'checkin_record' THEN
        UPDATE study_method 
        SET checkin_count = (
            SELECT COUNT(DISTINCT user_id) 
            FROM checkin_record 
            WHERE method_id = NEW.method_id
        )
        WHERE id = NEW.method_id;
    END IF;
    
    -- 更新评分和评价数
    IF TG_OP IN ('INSERT', 'UPDATE', 'DELETE') AND TG_TABLE_NAME = 'method_review' THEN
        UPDATE study_method 
        SET 
            rating = COALESCE((
                SELECT ROUND(AVG(rating), 1) 
                FROM method_review 
                WHERE method_id = COALESCE(NEW.method_id, OLD.method_id)
            ), 0.0),
            review_count = (
                SELECT COUNT(*) 
                FROM method_review 
                WHERE method_id = COALESCE(NEW.method_id, OLD.method_id)
            )
        WHERE id = COALESCE(NEW.method_id, OLD.method_id);
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 创建触发器自动更新统计信息
CREATE TRIGGER trigger_update_checkin_stats 
    AFTER INSERT ON checkin_record
    FOR EACH ROW EXECUTE FUNCTION update_method_stats();

CREATE TRIGGER trigger_update_review_stats 
    AFTER INSERT OR UPDATE OR DELETE ON method_review
    FOR EACH ROW EXECUTE FUNCTION update_method_stats();

-- 添加表注释
COMMENT ON TABLE study_method IS '学习方法表';
COMMENT ON TABLE checkin_record IS '打卡记录表';
COMMENT ON TABLE method_review IS '学习方法评价表';

-- 添加字段注释
COMMENT ON COLUMN study_method.category IS '方法分类：common-通用方法，tutor-导师独创';
COMMENT ON COLUMN study_method.type IS '适用类型，如"全学科""文科背诵"';
COMMENT ON COLUMN study_method.steps IS '方法步骤，JSON数组格式';
COMMENT ON COLUMN study_method.scene IS '推荐使用场景';
COMMENT ON COLUMN study_method.checkin_count IS '总打卡人数';
COMMENT ON COLUMN study_method.rating IS '平均评分（1-5分）';
COMMENT ON COLUMN study_method.review_count IS '评价总数';
COMMENT ON COLUMN study_method.status IS '状态：0-启用，1-下架';

COMMENT ON COLUMN checkin_record.checkin_type IS '打卡类型：正字打卡、计数打卡、时长打卡';
COMMENT ON COLUMN checkin_record.progress IS '打卡进度，如第几遍';
COMMENT ON COLUMN checkin_record.note IS '打卡心得备注';

COMMENT ON COLUMN method_review.rating IS '用户评分（1-5星）';
COMMENT ON COLUMN method_review.is_anonymous IS '是否匿名评价：0-否，1-是';

-- 创建复合索引优化常用查询
CREATE INDEX idx_study_method_category_status_rating ON study_method(category, status, rating DESC);
CREATE INDEX idx_checkin_record_user_date ON checkin_record(user_id, DATE(checkin_time AT TIME ZONE 'Asia/Shanghai'));

-- 添加 GIN 索引支持 JSONB 查询
CREATE INDEX idx_study_method_steps_gin ON study_method USING GIN (steps);

-- 创建视图：热门学习方法
CREATE VIEW v_popular_study_methods AS
SELECT 
    sm.*,
    CASE 
        WHEN sm.checkin_count >= 1000 THEN '热门'
        WHEN sm.checkin_count >= 100 THEN '推荐'
        ELSE '普通'
    END as popularity_level
FROM study_method sm
WHERE sm.status = 0
ORDER BY sm.checkin_count DESC, sm.rating DESC; 