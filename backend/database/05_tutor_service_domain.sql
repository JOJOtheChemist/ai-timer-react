-- ============================================================================
-- 四、导师与服务域（支撑导师页）
-- ============================================================================

-- 1. 导师表
CREATE TABLE tutor (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    type SMALLINT DEFAULT 0 CHECK (type IN (0, 1)), -- 0-普通导师，1-认证导师
    domain VARCHAR(200) NOT NULL, -- 擅长领域
    education VARCHAR(200) DEFAULT NULL, -- 教育背景
    experience VARCHAR(200) DEFAULT NULL, -- 上岸经历
    work_experience TEXT DEFAULT NULL, -- 工作经历
    philosophy TEXT DEFAULT NULL, -- 指导理念
    rating INTEGER DEFAULT 0 CHECK (rating >= 0 AND rating <= 100), -- 好评率
    student_count INTEGER DEFAULT 0 CHECK (student_count >= 0), -- 指导人数
    success_rate INTEGER DEFAULT 0 CHECK (success_rate >= 0 AND success_rate <= 100), -- 学员上岸率
    monthly_guide_count INTEGER DEFAULT 0 CHECK (monthly_guide_count >= 0), -- 近30天指导人数
    status SMALLINT DEFAULT 0 CHECK (status IN (0, 1, 2)), -- 0-正常，1-暂停服务，2-禁用
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. 导师服务表
CREATE TABLE tutor_service (
    id BIGSERIAL PRIMARY KEY,
    tutor_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL, -- 服务名称
    price INTEGER NOT NULL CHECK (price > 0), -- 价格（钻石）
    description TEXT NOT NULL, -- 服务描述
    unit VARCHAR(20) DEFAULT NULL, -- 单位，如"/篇"
    service_type VARCHAR(20) DEFAULT 'consultation' CHECK (service_type IN ('consultation', 'review', 'planning', 'correction')), -- 服务类型
    estimated_hours DECIMAL(3,1) DEFAULT NULL, -- 预计服务时长
    is_active SMALLINT DEFAULT 1 CHECK (is_active IN (0, 1)), -- 是否启用
    sort_order INTEGER DEFAULT 0, -- 排序
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tutor_id) REFERENCES tutor(id) ON DELETE CASCADE
);

-- 3. 导师评价表
CREATE TABLE tutor_review (
    id BIGSERIAL PRIMARY KEY,
    tutor_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    reviewer_name VARCHAR(50) NOT NULL, -- 评价者昵称
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5), -- 1-5星评分
    content TEXT NOT NULL, -- 评价内容
    attachment VARCHAR(200) DEFAULT NULL, -- 附件描述
    service_id BIGINT DEFAULT NULL, -- 关联的服务ID
    is_anonymous SMALLINT DEFAULT 0 CHECK (is_anonymous IN (0, 1)), -- 是否匿名
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tutor_id) REFERENCES tutor(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES tutor_service(id) ON DELETE SET NULL
);

-- 4. 导师服务订单表
CREATE TABLE tutor_service_order (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    tutor_id BIGINT NOT NULL,
    service_id BIGINT NOT NULL,
    amount INTEGER NOT NULL CHECK (amount > 0), -- 订单金额（钻石）
    status SMALLINT DEFAULT 0 CHECK (status IN (0, 1, 2, 3)), -- 0-待服务，1-服务中，2-已完成，3-已取消
    user_note TEXT DEFAULT NULL, -- 用户备注需求
    tutor_reply TEXT DEFAULT NULL, -- 导师回复
    completion_time TIMESTAMP WITH TIME ZONE DEFAULT NULL, -- 完成时间
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (tutor_id) REFERENCES tutor(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES tutor_service(id) ON DELETE CASCADE
);

-- 5. 导师专长标签表
CREATE TABLE tutor_expertise (
    id BIGSERIAL PRIMARY KEY,
    tutor_id BIGINT NOT NULL,
    tag_name VARCHAR(50) NOT NULL, -- 标签名，如"考研英语"、"四六级"
    tag_type VARCHAR(20) DEFAULT 'subject' CHECK (tag_type IN ('subject', 'level', 'skill')), -- 标签类型
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tutor_id) REFERENCES tutor(id) ON DELETE CASCADE,
    UNIQUE (tutor_id, tag_name)
);

-- 创建索引
CREATE INDEX idx_tutor_type ON tutor(type);
CREATE INDEX idx_tutor_status ON tutor(status);
CREATE INDEX idx_tutor_rating ON tutor(rating);
CREATE INDEX idx_tutor_student_count ON tutor(student_count);
CREATE INDEX idx_tutor_success_rate ON tutor(success_rate);
CREATE INDEX idx_tutor_monthly_guide_count ON tutor(monthly_guide_count);

CREATE INDEX idx_tutor_service_tutor_id ON tutor_service(tutor_id);
CREATE INDEX idx_tutor_service_price ON tutor_service(price);
CREATE INDEX idx_tutor_service_is_active ON tutor_service(is_active);
CREATE INDEX idx_tutor_service_service_type ON tutor_service(service_type);
CREATE INDEX idx_tutor_service_sort_order ON tutor_service(sort_order);

CREATE INDEX idx_tutor_review_tutor_id ON tutor_review(tutor_id);
CREATE INDEX idx_tutor_review_user_id ON tutor_review(user_id);
CREATE INDEX idx_tutor_review_rating ON tutor_review(rating);
CREATE INDEX idx_tutor_review_service_id ON tutor_review(service_id);
CREATE INDEX idx_tutor_review_create_time ON tutor_review(create_time);

CREATE INDEX idx_tutor_service_order_user_id ON tutor_service_order(user_id);
CREATE INDEX idx_tutor_service_order_tutor_id ON tutor_service_order(tutor_id);
CREATE INDEX idx_tutor_service_order_service_id ON tutor_service_order(service_id);
CREATE INDEX idx_tutor_service_order_status ON tutor_service_order(status);
CREATE INDEX idx_tutor_service_order_create_time ON tutor_service_order(create_time);

CREATE INDEX idx_tutor_expertise_tutor_id ON tutor_expertise(tutor_id);
CREATE INDEX idx_tutor_expertise_tag_name ON tutor_expertise(tag_name);
CREATE INDEX idx_tutor_expertise_tag_type ON tutor_expertise(tag_type);

-- 为相关表添加更新时间触发器
CREATE TRIGGER update_tutor_update_time BEFORE UPDATE ON tutor 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tutor_service_update_time BEFORE UPDATE ON tutor_service 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tutor_service_order_update_time BEFORE UPDATE ON tutor_service_order 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建函数用于更新导师统计信息
CREATE OR REPLACE FUNCTION update_tutor_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- 更新导师评分
    IF TG_OP IN ('INSERT', 'UPDATE', 'DELETE') AND TG_TABLE_NAME = 'tutor_review' THEN
        UPDATE tutor 
        SET rating = COALESCE((
            SELECT ROUND(AVG(rating) * 20, 0) -- 转换为百分制
            FROM tutor_review 
            WHERE tutor_id = COALESCE(NEW.tutor_id, OLD.tutor_id)
        ), 0)
        WHERE id = COALESCE(NEW.tutor_id, OLD.tutor_id);
    END IF;
    
    -- 更新导师服务统计
    IF TG_OP IN ('INSERT', 'UPDATE') AND TG_TABLE_NAME = 'tutor_service_order' THEN
        -- 更新学员总数（基于已完成订单）
        UPDATE tutor 
        SET student_count = (
            SELECT COUNT(DISTINCT user_id) 
            FROM tutor_service_order 
            WHERE tutor_id = NEW.tutor_id AND status = 2
        ),
        -- 更新近30天指导人数
        monthly_guide_count = (
            SELECT COUNT(DISTINCT user_id) 
            FROM tutor_service_order 
            WHERE tutor_id = NEW.tutor_id 
            AND status IN (1, 2) 
            AND create_time >= CURRENT_TIMESTAMP - INTERVAL '30 days'
        )
        WHERE id = NEW.tutor_id;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 创建触发器自动更新统计信息
CREATE TRIGGER trigger_update_tutor_review_stats 
    AFTER INSERT OR UPDATE OR DELETE ON tutor_review
    FOR EACH ROW EXECUTE FUNCTION update_tutor_stats();

CREATE TRIGGER trigger_update_tutor_order_stats 
    AFTER INSERT OR UPDATE ON tutor_service_order
    FOR EACH ROW EXECUTE FUNCTION update_tutor_stats();

-- 添加表注释
COMMENT ON TABLE tutor IS '导师表';
COMMENT ON TABLE tutor_service IS '导师服务表';
COMMENT ON TABLE tutor_review IS '导师评价表';
COMMENT ON TABLE tutor_service_order IS '导师服务订单表';
COMMENT ON TABLE tutor_expertise IS '导师专长标签表';

-- 添加字段注释
COMMENT ON COLUMN tutor.type IS '导师类型：0-普通导师，1-认证导师';
COMMENT ON COLUMN tutor.rating IS '好评率（0-100）';
COMMENT ON COLUMN tutor.student_count IS '累计指导学员数';
COMMENT ON COLUMN tutor.success_rate IS '学员上岸率（0-100）';
COMMENT ON COLUMN tutor.monthly_guide_count IS '近30天指导人数';
COMMENT ON COLUMN tutor.status IS '状态：0-正常，1-暂停服务，2-禁用';

COMMENT ON COLUMN tutor_service.price IS '服务价格（钻石）';
COMMENT ON COLUMN tutor_service.service_type IS '服务类型：consultation-咨询，review-点评，planning-规划，correction-批改';
COMMENT ON COLUMN tutor_service.estimated_hours IS '预计服务时长（小时）';
COMMENT ON COLUMN tutor_service.is_active IS '是否启用：0-否，1-是';

COMMENT ON COLUMN tutor_review.rating IS '评分（1-5星）';
COMMENT ON COLUMN tutor_review.is_anonymous IS '是否匿名评价：0-否，1-是';

COMMENT ON COLUMN tutor_service_order.status IS '订单状态：0-待服务，1-服务中，2-已完成，3-已取消';
COMMENT ON COLUMN tutor_service_order.amount IS '订单金额（钻石）';

COMMENT ON COLUMN tutor_expertise.tag_type IS '标签类型：subject-学科，level-等级，skill-技能';

-- 创建复合索引优化常用查询
CREATE INDEX idx_tutor_type_status_rating ON tutor(type, status, rating DESC);
CREATE INDEX idx_tutor_service_tutor_active_price ON tutor_service(tutor_id, is_active, price);
CREATE INDEX idx_tutor_service_order_user_status_time ON tutor_service_order(user_id, status, create_time DESC);

-- 创建视图：导师服务概览
CREATE VIEW v_tutor_service_overview AS
SELECT 
    t.id as tutor_id,
    t.username,
    t.type,
    t.rating,
    t.student_count,
    t.success_rate,
    COUNT(ts.id) as service_count,
    MIN(ts.price) as min_price,
    MAX(ts.price) as max_price,
    AVG(ts.price) as avg_price
FROM tutor t
LEFT JOIN tutor_service ts ON t.id = ts.tutor_id AND ts.is_active = 1
WHERE t.status = 0
GROUP BY t.id, t.username, t.type, t.rating, t.student_count, t.success_rate
ORDER BY t.rating DESC, t.student_count DESC; 