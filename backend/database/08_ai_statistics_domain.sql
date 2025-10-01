-- ============================================================================
-- 七、AI与统计域（支撑AI对话、统计功能）
-- ============================================================================

-- 1. AI聊天记录表
CREATE TABLE ai_chat_record (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    session_id VARCHAR(100) NOT NULL, -- 会话ID，用于关联同一次对话
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'ai')), -- 角色
    content TEXT NOT NULL, -- 消息内容
    is_analysis SMALLINT DEFAULT 0 CHECK (is_analysis IN (0, 1)), -- 是否分析型回复
    analysis_tags JSONB DEFAULT NULL, -- 分析标签，如["复习不足","时间碎片化"]
    related_data JSONB DEFAULT NULL, -- 相关数据（如时间表数据、统计数据）
    token_count INTEGER DEFAULT 0 CHECK (token_count >= 0), -- 消耗的token数
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 2. AI分析记录表
CREATE TABLE ai_analysis_record (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    analysis_type VARCHAR(20) NOT NULL CHECK (analysis_type IN ('schedule', 'habit', 'progress', 'efficiency')), -- 分析类型
    analysis_tags JSONB DEFAULT '[]'::jsonb, -- 分析标签数组
    analysis_content TEXT NOT NULL, -- 分析内容
    analysis_data JSONB DEFAULT NULL, -- 分析数据（图表数据、统计结果等）
    confidence_score DECIMAL(3,2) DEFAULT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1), -- 置信度
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expire_time TIMESTAMP WITH TIME ZONE DEFAULT NULL, -- 过期时间
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 3. AI推荐表
CREATE TABLE ai_recommendation (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    rec_type VARCHAR(20) NOT NULL CHECK (rec_type IN ('method', 'case', 'tutor', 'schedule', 'task')), -- 推荐类型
    related_id BIGINT DEFAULT NULL, -- 关联ID
    title VARCHAR(200) NOT NULL, -- 推荐标题
    description TEXT NOT NULL, -- 推荐描述
    reason TEXT DEFAULT NULL, -- 推荐理由
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5), -- 优先级1-5
    is_accepted SMALLINT DEFAULT 0 CHECK (is_accepted IN (0, 1, 2)), -- 0-未处理，1-采纳，2-拒绝
    feedback TEXT DEFAULT NULL, -- 用户反馈
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expire_time TIMESTAMP WITH TIME ZONE DEFAULT NULL, -- 过期时间
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 4. 周统计表
CREATE TABLE statistic_weekly (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    year_week VARCHAR(20) NOT NULL, -- 年周，如"2025-38"
    total_study_hours DECIMAL(10,1) DEFAULT 0.0 CHECK (total_study_hours >= 0), -- 总学习时长
    high_freq_complete VARCHAR(20) DEFAULT '0/0', -- 高频任务完成情况，如"4/5"
    overcome_complete VARCHAR(20) DEFAULT '0/0', -- 待克服任务完成情况，如"1/2"
    ai_accept_rate INTEGER DEFAULT 0 CHECK (ai_accept_rate >= 0 AND ai_accept_rate <= 100), -- AI推荐采纳率
    category_hours JSONB DEFAULT '{}'::jsonb, -- 各类型时长，如{"学习":8.5,"生活":5,"工作":4}
    mood_distribution JSONB DEFAULT '{}'::jsonb, -- 心情分布统计
    efficiency_score DECIMAL(3,1) DEFAULT NULL, -- 效率评分
    improvement_rate DECIMAL(5,2) DEFAULT NULL, -- 相比上周的改进率
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    UNIQUE (user_id, year_week) -- 每个用户每周只有一条记录
);

-- 5. 日统计表
CREATE TABLE statistic_daily (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    date DATE NOT NULL,
    total_study_hours DECIMAL(5,1) DEFAULT 0.0 CHECK (total_study_hours >= 0), -- 当日总学习时长
    completed_tasks INTEGER DEFAULT 0 CHECK (completed_tasks >= 0), -- 完成任务数
    total_tasks INTEGER DEFAULT 0 CHECK (total_tasks >= 0), -- 总任务数
    completion_rate DECIMAL(5,2) DEFAULT 0.0 CHECK (completion_rate >= 0 AND completion_rate <= 100), -- 完成率
    focus_time DECIMAL(5,1) DEFAULT 0.0, -- 专注时长
    break_time DECIMAL(5,1) DEFAULT 0.0, -- 休息时长
    dominant_mood VARCHAR(20) DEFAULT NULL, -- 主要心情
    category_hours JSONB DEFAULT '{}'::jsonb, -- 各类型时长分布
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    UNIQUE (user_id, date) -- 每个用户每天只有一条记录
);

-- 6. 用户行为日志表
CREATE TABLE user_behavior_log (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    action_type VARCHAR(50) NOT NULL, -- 行为类型，如login、create_task、complete_task等
    action_detail JSONB DEFAULT NULL, -- 行为详情
    page_path VARCHAR(100) DEFAULT NULL, -- 页面路径
    ip_address INET DEFAULT NULL, -- IP地址
    user_agent TEXT DEFAULT NULL, -- 用户代理
    session_id VARCHAR(100) DEFAULT NULL, -- 会话ID
    duration INTEGER DEFAULT NULL, -- 持续时间（秒）
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 7. 系统性能监控表
CREATE TABLE system_performance (
    id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(50) NOT NULL, -- 指标名称
    metric_value DECIMAL(10,2) NOT NULL, -- 指标值
    metric_unit VARCHAR(20) DEFAULT NULL, -- 单位
    tags JSONB DEFAULT NULL, -- 标签
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_ai_chat_record_user_id ON ai_chat_record(user_id);
CREATE INDEX idx_ai_chat_record_session_id ON ai_chat_record(session_id);
CREATE INDEX idx_ai_chat_record_role ON ai_chat_record(role);
CREATE INDEX idx_ai_chat_record_is_analysis ON ai_chat_record(is_analysis);
CREATE INDEX idx_ai_chat_record_create_time ON ai_chat_record(create_time);

CREATE INDEX idx_ai_analysis_record_user_id ON ai_analysis_record(user_id);
CREATE INDEX idx_ai_analysis_record_analysis_type ON ai_analysis_record(analysis_type);
CREATE INDEX idx_ai_analysis_record_create_time ON ai_analysis_record(create_time);
CREATE INDEX idx_ai_analysis_record_expire_time ON ai_analysis_record(expire_time);

CREATE INDEX idx_ai_recommendation_user_id ON ai_recommendation(user_id);
CREATE INDEX idx_ai_recommendation_rec_type ON ai_recommendation(rec_type);
CREATE INDEX idx_ai_recommendation_related_id ON ai_recommendation(related_id);
CREATE INDEX idx_ai_recommendation_is_accepted ON ai_recommendation(is_accepted);
CREATE INDEX idx_ai_recommendation_priority ON ai_recommendation(priority);
CREATE INDEX idx_ai_recommendation_create_time ON ai_recommendation(create_time);

CREATE INDEX idx_statistic_weekly_user_id ON statistic_weekly(user_id);
CREATE INDEX idx_statistic_weekly_year_week ON statistic_weekly(year_week);
CREATE INDEX idx_statistic_weekly_total_hours ON statistic_weekly(total_study_hours);
CREATE INDEX idx_statistic_weekly_create_time ON statistic_weekly(create_time);

CREATE INDEX idx_statistic_daily_user_id ON statistic_daily(user_id);
CREATE INDEX idx_statistic_daily_date ON statistic_daily(date);
CREATE INDEX idx_statistic_daily_user_date ON statistic_daily(user_id, date);
CREATE INDEX idx_statistic_daily_completion_rate ON statistic_daily(completion_rate);

CREATE INDEX idx_user_behavior_log_user_id ON user_behavior_log(user_id);
CREATE INDEX idx_user_behavior_log_action_type ON user_behavior_log(action_type);
CREATE INDEX idx_user_behavior_log_session_id ON user_behavior_log(session_id);
CREATE INDEX idx_user_behavior_log_create_time ON user_behavior_log(create_time);

CREATE INDEX idx_system_performance_metric_name ON system_performance(metric_name);
CREATE INDEX idx_system_performance_create_time ON system_performance(create_time);

-- 添加 GIN 索引支持 JSONB 查询
CREATE INDEX idx_ai_chat_record_analysis_tags_gin ON ai_chat_record USING GIN (analysis_tags);
CREATE INDEX idx_ai_analysis_record_tags_gin ON ai_analysis_record USING GIN (analysis_tags);
CREATE INDEX idx_ai_analysis_record_data_gin ON ai_analysis_record USING GIN (analysis_data);
CREATE INDEX idx_statistic_weekly_category_hours_gin ON statistic_weekly USING GIN (category_hours);
CREATE INDEX idx_statistic_daily_category_hours_gin ON statistic_daily USING GIN (category_hours);
CREATE INDEX idx_user_behavior_log_detail_gin ON user_behavior_log USING GIN (action_detail);
CREATE INDEX idx_system_performance_tags_gin ON system_performance USING GIN (tags);

-- 创建分区表（按时间分区）
-- 为用户行为日志创建按月分区
CREATE TABLE user_behavior_log_y2025m01 PARTITION OF user_behavior_log
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- 创建函数用于自动创建分区
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name TEXT, start_date DATE)
RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    end_date DATE;
BEGIN
    partition_name := table_name || '_y' || EXTRACT(YEAR FROM start_date) || 'm' || LPAD(EXTRACT(MONTH FROM start_date)::TEXT, 2, '0');
    end_date := start_date + INTERVAL '1 month';
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
                   partition_name, table_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;

-- 创建函数用于计算用户统计数据
CREATE OR REPLACE FUNCTION calculate_user_daily_stats(target_user_id BIGINT, target_date DATE)
RETURNS VOID AS $$
DECLARE
    total_hours DECIMAL(5,1);
    completed_count INTEGER;
    total_count INTEGER;
    completion_pct DECIMAL(5,2);
    category_data JSONB;
BEGIN
    -- 计算当日总学习时长和任务完成情况
    SELECT 
        COALESCE(SUM(
            CASE 
                WHEN ts.status = 'completed' AND t.type = 'study' THEN 
                    EXTRACT(EPOCH FROM (
                        (split_part(ts.time_range, '-', 2) || ':00')::TIME - 
                        (split_part(ts.time_range, '-', 1) || ':00')::TIME
                    )) / 3600.0
                ELSE 0 
            END
        ), 0),
        COUNT(CASE WHEN ts.status = 'completed' THEN 1 END),
        COUNT(*)
    INTO total_hours, completed_count, total_count
    FROM time_slot ts
    LEFT JOIN task t ON ts.task_id = t.id
    WHERE ts.user_id = target_user_id AND ts.date = target_date;
    
    -- 计算完成率
    completion_pct := CASE WHEN total_count > 0 THEN (completed_count::DECIMAL / total_count) * 100 ELSE 0 END;
    
    -- 计算各类型时长分布
    SELECT jsonb_object_agg(
        COALESCE(t.type, 'other'),
        COALESCE(SUM(
            EXTRACT(EPOCH FROM (
                (split_part(ts.time_range, '-', 2) || ':00')::TIME - 
                (split_part(ts.time_range, '-', 1) || ':00')::TIME
            )) / 3600.0
        ), 0)
    )
    INTO category_data
    FROM time_slot ts
    LEFT JOIN task t ON ts.task_id = t.id
    WHERE ts.user_id = target_user_id 
    AND ts.date = target_date 
    AND ts.status = 'completed'
    GROUP BY t.type;
    
    -- 插入或更新统计数据
    INSERT INTO statistic_daily (
        user_id, date, total_study_hours, completed_tasks, total_tasks, 
        completion_rate, category_hours
    ) VALUES (
        target_user_id, target_date, total_hours, completed_count, total_count,
        completion_pct, COALESCE(category_data, '{}'::jsonb)
    )
    ON CONFLICT (user_id, date) 
    DO UPDATE SET
        total_study_hours = EXCLUDED.total_study_hours,
        completed_tasks = EXCLUDED.completed_tasks,
        total_tasks = EXCLUDED.total_tasks,
        completion_rate = EXCLUDED.completion_rate,
        category_hours = EXCLUDED.category_hours;
END;
$$ LANGUAGE plpgsql;

-- 创建函数用于清理过期数据
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS VOID AS $$
BEGIN
    -- 清理过期的AI分析记录
    DELETE FROM ai_analysis_record 
    WHERE expire_time IS NOT NULL AND expire_time < CURRENT_TIMESTAMP;
    
    -- 清理过期的AI推荐
    DELETE FROM ai_recommendation 
    WHERE expire_time IS NOT NULL AND expire_time < CURRENT_TIMESTAMP;
    
    -- 清理90天前的AI聊天记录
    DELETE FROM ai_chat_record 
    WHERE create_time < CURRENT_TIMESTAMP - INTERVAL '90 days';
    
    -- 清理180天前的用户行为日志
    DELETE FROM user_behavior_log 
    WHERE create_time < CURRENT_TIMESTAMP - INTERVAL '180 days';
    
    -- 清理30天前的系统性能监控数据
    DELETE FROM system_performance 
    WHERE create_time < CURRENT_TIMESTAMP - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- 添加表注释
COMMENT ON TABLE ai_chat_record IS 'AI聊天记录表';
COMMENT ON TABLE ai_analysis_record IS 'AI分析记录表';
COMMENT ON TABLE ai_recommendation IS 'AI推荐表';
COMMENT ON TABLE statistic_weekly IS '周统计表';
COMMENT ON TABLE statistic_daily IS '日统计表';
COMMENT ON TABLE user_behavior_log IS '用户行为日志表';
COMMENT ON TABLE system_performance IS '系统性能监控表';

-- 添加字段注释
COMMENT ON COLUMN ai_chat_record.role IS '角色：user-用户，ai-AI助手';
COMMENT ON COLUMN ai_chat_record.is_analysis IS '是否分析型回复：0-否，1-是';
COMMENT ON COLUMN ai_chat_record.session_id IS '会话ID，用于关联同一次对话';

COMMENT ON COLUMN ai_analysis_record.analysis_type IS '分析类型：schedule-时间表，habit-习惯，progress-进度，efficiency-效率';
COMMENT ON COLUMN ai_analysis_record.confidence_score IS '分析置信度（0-1）';

COMMENT ON COLUMN ai_recommendation.rec_type IS '推荐类型：method-学习方法，case-案例，tutor-导师，schedule-时间表，task-任务';
COMMENT ON COLUMN ai_recommendation.is_accepted IS '处理状态：0-未处理，1-采纳，2-拒绝';
COMMENT ON COLUMN ai_recommendation.priority IS '优先级：1-5，数字越大优先级越高';

COMMENT ON COLUMN statistic_weekly.year_week IS '年周，格式：YYYY-WW';
COMMENT ON COLUMN statistic_weekly.high_freq_complete IS '高频任务完成情况，格式：已完成/总数';
COMMENT ON COLUMN statistic_weekly.ai_accept_rate IS 'AI推荐采纳率（百分比）';

COMMENT ON COLUMN user_behavior_log.action_type IS '行为类型：login、logout、create_task、complete_task等';
COMMENT ON COLUMN user_behavior_log.duration IS '行为持续时间（秒）';

-- 创建复合索引优化常用查询
CREATE INDEX idx_ai_chat_record_user_session_time ON ai_chat_record(user_id, session_id, create_time);
CREATE INDEX idx_statistic_daily_user_date_hours ON statistic_daily(user_id, date, total_study_hours);
CREATE INDEX idx_user_behavior_log_user_action_time ON user_behavior_log(user_id, action_type, create_time);

-- 创建视图：用户学习趋势
CREATE VIEW v_user_study_trend AS
SELECT 
    sd.user_id,
    sd.date,
    sd.total_study_hours,
    sd.completion_rate,
    LAG(sd.total_study_hours) OVER (PARTITION BY sd.user_id ORDER BY sd.date) as prev_day_hours,
    AVG(sd.total_study_hours) OVER (
        PARTITION BY sd.user_id 
        ORDER BY sd.date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as week_avg_hours
FROM statistic_daily sd
ORDER BY sd.user_id, sd.date DESC;

-- 创建视图：AI推荐效果统计
CREATE VIEW v_ai_recommendation_stats AS
SELECT 
    rec_type,
    COUNT(*) as total_recommendations,
    COUNT(CASE WHEN is_accepted = 1 THEN 1 END) as accepted_count,
    COUNT(CASE WHEN is_accepted = 2 THEN 1 END) as rejected_count,
    ROUND(
        COUNT(CASE WHEN is_accepted = 1 THEN 1 END)::DECIMAL / 
        NULLIF(COUNT(CASE WHEN is_accepted IN (1,2) THEN 1 END), 0) * 100, 
        2
    ) as acceptance_rate
FROM ai_recommendation
GROUP BY rec_type
ORDER BY acceptance_rate DESC; 