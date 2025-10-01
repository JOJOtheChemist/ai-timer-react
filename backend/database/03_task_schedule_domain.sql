-- ============================================================================
-- 二、任务与时间表域（支撑首页核心功能）
-- ============================================================================

-- 1. 任务表
CREATE TABLE task (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('study', 'life', 'work')),
    category VARCHAR(20) DEFAULT NULL,
    weekly_hours DECIMAL(5,1) DEFAULT 0.0 CHECK (weekly_hours >= 0),
    is_high_frequency SMALLINT DEFAULT 0 CHECK (is_high_frequency IN (0, 1)),
    is_overcome SMALLINT DEFAULT 0 CHECK (is_overcome IN (0, 1)),
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 2. 子任务表
CREATE TABLE subtask (
    id BIGSERIAL PRIMARY KEY,
    task_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL, -- 冗余字段便于查询
    name VARCHAR(100) NOT NULL,
    hours DECIMAL(5,1) DEFAULT 0.0 CHECK (hours >= 0),
    is_high_frequency SMALLINT DEFAULT 0 CHECK (is_high_frequency IN (0, 1)),
    is_overcome SMALLINT DEFAULT 0 CHECK (is_overcome IN (0, 1)),
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 3. 时间段表
CREATE TABLE time_slot (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    date DATE NOT NULL,
    time_range VARCHAR(20) NOT NULL, -- 格式：07:30-08:30
    task_id BIGINT DEFAULT NULL,
    subtask_id BIGINT DEFAULT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('completed', 'in-progress', 'pending', 'empty')),
    is_ai_recommended SMALLINT DEFAULT 0 CHECK (is_ai_recommended IN (0, 1)),
    note TEXT DEFAULT NULL,
    ai_tip TEXT DEFAULT NULL,
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE SET NULL,
    FOREIGN KEY (subtask_id) REFERENCES subtask(id) ON DELETE SET NULL
);

-- 4. 心情记录表
CREATE TABLE mood_record (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    time_slot_id BIGINT UNIQUE NOT NULL, -- 一对一关系
    mood VARCHAR(20) NOT NULL CHECK (mood IN ('happy', 'focused', 'tired', 'stressed', 'excited')),
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (time_slot_id) REFERENCES time_slot(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_task_user_id ON task(user_id);
CREATE INDEX idx_task_type ON task(type);
CREATE INDEX idx_task_is_high_frequency ON task(is_high_frequency);
CREATE INDEX idx_task_is_overcome ON task(is_overcome);
CREATE INDEX idx_task_create_time ON task(create_time);

CREATE INDEX idx_subtask_task_id ON subtask(task_id);
CREATE INDEX idx_subtask_user_id ON subtask(user_id);
CREATE INDEX idx_subtask_is_high_frequency ON subtask(is_high_frequency);
CREATE INDEX idx_subtask_is_overcome ON subtask(is_overcome);

CREATE INDEX idx_time_slot_user_id ON time_slot(user_id);
CREATE INDEX idx_time_slot_date ON time_slot(date);
CREATE INDEX idx_time_slot_user_date ON time_slot(user_id, date);
CREATE INDEX idx_time_slot_task_id ON time_slot(task_id);
CREATE INDEX idx_time_slot_subtask_id ON time_slot(subtask_id);
CREATE INDEX idx_time_slot_status ON time_slot(status);
CREATE INDEX idx_time_slot_is_ai_recommended ON time_slot(is_ai_recommended);

CREATE INDEX idx_mood_record_user_id ON mood_record(user_id);
CREATE INDEX idx_mood_record_time_slot_id ON mood_record(time_slot_id);
CREATE INDEX idx_mood_record_mood ON mood_record(mood);
CREATE INDEX idx_mood_record_create_time ON mood_record(create_time);

-- 为相关表添加更新时间触发器
CREATE TRIGGER update_task_update_time BEFORE UPDATE ON task 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subtask_update_time BEFORE UPDATE ON subtask 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_time_slot_update_time BEFORE UPDATE ON time_slot 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 添加表注释
COMMENT ON TABLE task IS '任务表';
COMMENT ON TABLE subtask IS '子任务表';
COMMENT ON TABLE time_slot IS '时间段表';
COMMENT ON TABLE mood_record IS '心情记录表';

-- 添加字段注释
COMMENT ON COLUMN task.type IS '任务类型：study-学习，life-生活，work-工作';
COMMENT ON COLUMN task.is_high_frequency IS '是否高频任务：0-否，1-是';
COMMENT ON COLUMN task.is_overcome IS '是否待克服任务：0-否，1-是';
COMMENT ON COLUMN task.weekly_hours IS '本周时长（小时）';

COMMENT ON COLUMN subtask.hours IS '子任务时长（小时）';
COMMENT ON COLUMN subtask.is_high_frequency IS '是否高频子任务：0-否，1-是';
COMMENT ON COLUMN subtask.is_overcome IS '是否待克服子任务：0-否，1-是';

COMMENT ON COLUMN time_slot.time_range IS '时间段，格式：07:30-08:30';
COMMENT ON COLUMN time_slot.status IS '状态：completed-已完成，in-progress-进行中，pending-未开始，empty-空白';
COMMENT ON COLUMN time_slot.is_ai_recommended IS '是否AI推荐：0-否，1-是';

COMMENT ON COLUMN mood_record.mood IS '心情：happy-愉快，focused-专注，tired-疲惫，stressed-压力，excited-兴奋';

-- 创建复合索引优化常用查询
CREATE INDEX idx_time_slot_user_date_range ON time_slot(user_id, date, time_range);
CREATE INDEX idx_task_user_type_frequency ON task(user_id, type, is_high_frequency);

-- 添加约束确保时间段格式正确
ALTER TABLE time_slot ADD CONSTRAINT check_time_range_format 
    CHECK (time_range ~ '^\d{2}:\d{2}-\d{2}:\d{2}$');

-- 添加约束确保日期不能是未来太远的日期（比如不超过1年后）
ALTER TABLE time_slot ADD CONSTRAINT check_date_reasonable 
    CHECK (date >= CURRENT_DATE - INTERVAL '1 year' AND date <= CURRENT_DATE + INTERVAL '1 year'); 