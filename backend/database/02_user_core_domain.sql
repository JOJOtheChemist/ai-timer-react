-- ============================================================================
-- 一、用户核心域（支撑个人主页、登录、权限）
-- ============================================================================

-- 1. 用户基础信息表
CREATE TABLE "user" (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    goal VARCHAR(100) DEFAULT NULL,
    major VARCHAR(50) DEFAULT NULL,
    join_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status SMALLINT DEFAULT 0 CHECK (status IN (0, 1)), -- 0-正常，1-禁用
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. 用户资产表
CREATE TABLE user_asset (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    diamond_count INTEGER DEFAULT 0 CHECK (diamond_count >= 0),
    last_consume_time TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 3. 用户详细资料表
CREATE TABLE user_profile (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    real_name VARCHAR(50) DEFAULT NULL,
    bio TEXT DEFAULT NULL,
    total_study_hours DECIMAL(10,1) DEFAULT 0.0 CHECK (total_study_hours >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 4. 用户消息设置表
CREATE TABLE user_message_setting (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    reminder_type SMALLINT DEFAULT 0 CHECK (reminder_type IN (0, 1)), -- 0-仅APP内，1-推送通知
    keep_days INTEGER DEFAULT 7 CHECK (keep_days > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 5. 用户关系表
CREATE TABLE user_relation (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    target_user_id BIGINT NOT NULL,
    relation_type SMALLINT NOT NULL CHECK (relation_type IN (0, 1, 2)), -- 0-关注导师，1-粉丝，2-普通好友
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (target_user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    UNIQUE (user_id, target_user_id, relation_type),
    CHECK (user_id != target_user_id) -- 防止自己关注自己
);

-- 创建索引
CREATE INDEX idx_user_phone ON "user"(phone);
CREATE INDEX idx_user_status ON "user"(status);
CREATE INDEX idx_user_join_time ON "user"(join_time);

CREATE INDEX idx_user_asset_user_id ON user_asset(user_id);
CREATE INDEX idx_user_asset_diamond_count ON user_asset(diamond_count);

CREATE INDEX idx_user_profile_user_id ON user_profile(user_id);
CREATE INDEX idx_user_profile_total_study_hours ON user_profile(total_study_hours);

CREATE INDEX idx_user_message_setting_user_id ON user_message_setting(user_id);

CREATE INDEX idx_user_relation_user_id ON user_relation(user_id);
CREATE INDEX idx_user_relation_target_user_id ON user_relation(target_user_id);
CREATE INDEX idx_user_relation_type ON user_relation(relation_type);
CREATE INDEX idx_user_relation_create_time ON user_relation(create_time);

-- 创建触发器函数用于自动更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为相关表添加更新时间触发器
CREATE TRIGGER update_user_updated_at BEFORE UPDATE ON "user" 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_asset_updated_at BEFORE UPDATE ON user_asset 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profile_updated_at BEFORE UPDATE ON user_profile 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_message_setting_updated_at BEFORE UPDATE ON user_message_setting 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 添加表注释
COMMENT ON TABLE "user" IS '用户基础信息表';
COMMENT ON TABLE user_asset IS '用户资产表';
COMMENT ON TABLE user_profile IS '用户详细资料表';
COMMENT ON TABLE user_message_setting IS '用户消息设置表';
COMMENT ON TABLE user_relation IS '用户关系表';

-- 添加字段注释
COMMENT ON COLUMN "user".status IS '账号状态：0-正常，1-禁用';
COMMENT ON COLUMN user_asset.diamond_count IS '钻石数量';
COMMENT ON COLUMN user_profile.total_study_hours IS '总学习时长（小时）';
COMMENT ON COLUMN user_message_setting.reminder_type IS '提醒方式：0-仅APP内，1-推送通知';
COMMENT ON COLUMN user_message_setting.keep_days IS '未读消息保留天数';
COMMENT ON COLUMN user_relation.relation_type IS '关系类型：0-关注导师，1-粉丝，2-普通好友'; 