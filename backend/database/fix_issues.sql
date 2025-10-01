-- ============================================================================
-- 修复数据库创建中的问题
-- ============================================================================

\c ai_time_management;

-- 1. 修复 checkin_record 表
DROP TABLE IF EXISTS checkin_record CASCADE;

CREATE TABLE checkin_record (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    method_id BIGINT NOT NULL,
    checkin_type VARCHAR(20) NOT NULL CHECK (checkin_type IN ('正字打卡', '计数打卡', '时长打卡')),
    progress INTEGER DEFAULT 1 CHECK (progress >= 1),
    note TEXT DEFAULT NULL,
    checkin_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (method_id) REFERENCES study_method(id) ON DELETE CASCADE
);

-- 添加唯一约束（修复语法）
ALTER TABLE checkin_record 
ADD CONSTRAINT unique_user_method_daily 
UNIQUE (user_id, method_id, DATE(checkin_time AT TIME ZONE 'Asia/Shanghai'));

-- 创建索引
CREATE INDEX idx_checkin_record_user_id ON checkin_record(user_id);
CREATE INDEX idx_checkin_record_method_id ON checkin_record(method_id);
CREATE INDEX idx_checkin_record_checkin_type ON checkin_record(checkin_type);
CREATE INDEX idx_checkin_record_checkin_time ON checkin_record(checkin_time);
CREATE INDEX idx_checkin_record_user_method ON checkin_record(user_id, method_id);
CREATE INDEX idx_checkin_record_user_date ON checkin_record(user_id, DATE(checkin_time AT TIME ZONE 'Asia/Shanghai'));

-- 添加表注释
COMMENT ON TABLE checkin_record IS '打卡记录表';
COMMENT ON COLUMN checkin_record.checkin_type IS '打卡类型：正字打卡、计数打卡、时长打卡';
COMMENT ON COLUMN checkin_record.progress IS '打卡进度，如第几遍';
COMMENT ON COLUMN checkin_record.note IS '打卡心得备注';

-- 2. 重新创建相关触发器
CREATE TRIGGER trigger_update_checkin_stats 
    AFTER INSERT ON checkin_record
    FOR EACH ROW EXECUTE FUNCTION update_method_stats();

CREATE TRIGGER trigger_auto_check_badges_checkin 
    AFTER INSERT ON checkin_record
    FOR EACH ROW EXECUTE FUNCTION auto_check_badges();

-- 3. 修复全文搜索索引（使用简单配置）
DROP INDEX IF EXISTS idx_moment_content_search;
DROP INDEX IF EXISTS idx_message_content_search;

CREATE INDEX idx_moment_content_search ON moment USING GIN (to_tsvector('simple', content));
CREATE INDEX idx_message_content_search ON message USING GIN (to_tsvector('simple', content));

-- 4. 修复用户行为日志分区表
DROP TABLE IF EXISTS user_behavior_log_y2025m01;

-- 重新创建为分区表
ALTER TABLE user_behavior_log RENAME TO user_behavior_log_old;

CREATE TABLE user_behavior_log (
    id BIGSERIAL,
    user_id BIGINT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    action_detail JSONB DEFAULT NULL,
    page_path VARCHAR(100) DEFAULT NULL,
    ip_address INET DEFAULT NULL,
    user_agent TEXT DEFAULT NULL,
    session_id VARCHAR(100) DEFAULT NULL,
    duration INTEGER DEFAULT NULL,
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
) PARTITION BY RANGE (create_time);

-- 创建2025年1月分区
CREATE TABLE user_behavior_log_y2025m01 PARTITION OF user_behavior_log
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- 创建2025年2月分区
CREATE TABLE user_behavior_log_y2025m02 PARTITION OF user_behavior_log
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- 重新创建索引
CREATE INDEX idx_user_behavior_log_user_id ON user_behavior_log(user_id);
CREATE INDEX idx_user_behavior_log_action_type ON user_behavior_log(action_type);
CREATE INDEX idx_user_behavior_log_session_id ON user_behavior_log(session_id);
CREATE INDEX idx_user_behavior_log_create_time ON user_behavior_log(create_time);
CREATE INDEX idx_user_behavior_log_detail_gin ON user_behavior_log USING GIN (action_detail);
CREATE INDEX idx_user_behavior_log_user_action_time ON user_behavior_log(user_id, action_type, create_time);

-- 删除旧表
DROP TABLE user_behavior_log_old;

-- 5. 修复性能建议函数
CREATE OR REPLACE FUNCTION get_performance_recommendations()
RETURNS TABLE(
    recommendation_type TEXT,
    table_name TEXT,
    suggestion TEXT,
    priority INTEGER
) AS $$
BEGIN
    -- 检查缺失的索引
    RETURN QUERY
    SELECT 
        'missing_index'::TEXT,
        'time_slot'::TEXT,
        '建议在 (user_id, date, status) 上创建复合索引以优化时间表查询'::TEXT,
        1::INTEGER
    WHERE NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'time_slot' 
        AND indexname LIKE '%user_date_status%'
    );
    
    -- 检查表大小和分区建议
    RETURN QUERY
    SELECT 
        'partitioning'::TEXT,
        pt.schemaname || '.' || pt.tablename,
        '表大小超过1GB，建议考虑分区: ' || pg_size_pretty(pg_total_relation_size(pt.schemaname||'.'||pt.tablename)),
        2::INTEGER
    FROM pg_tables pt
    WHERE pt.schemaname = 'public'
    AND pg_total_relation_size(pt.schemaname||'.'||pt.tablename) > 1024*1024*1024;
    
    -- 检查统计信息更新
    RETURN QUERY
    SELECT 
        'statistics'::TEXT,
        pst.schemaname || '.' || pst.relname,
        '表统计信息可能过期，建议运行 ANALYZE'::TEXT,
        3::INTEGER
    FROM pg_stat_user_tables pst
    WHERE pst.schemaname = 'public'
    AND (pst.last_analyze IS NULL OR pst.last_analyze < CURRENT_TIMESTAMP - INTERVAL '7 days')
    AND pst.n_tup_ins + pst.n_tup_upd + pst.n_tup_del > 1000;
    
END;
$$ LANGUAGE plpgsql;

-- 6. 更新视图中的表分类
CREATE OR REPLACE VIEW v_system_overview AS
SELECT 
    'users' as metric_type,
    COUNT(*)::TEXT as metric_value,
    '总用户数' as description
FROM "user"
WHERE status = 0

UNION ALL

SELECT 
    'active_users_today',
    COUNT(DISTINCT user_id)::TEXT,
    '今日活跃用户'
FROM user_behavior_log
WHERE create_time >= CURRENT_DATE

UNION ALL

SELECT 
    'total_study_hours',
    COALESCE(ROUND(SUM(total_study_hours), 1), 0)::TEXT,
    '总学习时长（小时）'
FROM user_profile

UNION ALL

SELECT 
    'total_tasks',
    COUNT(*)::TEXT,
    '总任务数'
FROM task

UNION ALL

SELECT 
    'total_moments',
    COUNT(*)::TEXT,
    '总动态数'
FROM moment
WHERE status = 0

UNION ALL

SELECT 
    'total_badges_awarded',
    COUNT(*)::TEXT,
    '已颁发徽章数'
FROM user_badge;

-- 7. 运行统计信息更新
ANALYZE;

\echo '数据库问题修复完成！';
\echo '- checkin_record 表已重新创建';
\echo '- 全文搜索索引已修复';
\echo '- 分区表已正确配置';
\echo '- 性能函数已修复';
\echo '- 统计信息已更新';

-- 验证修复结果
SELECT 'checkin_record' as table_name, COUNT(*) as record_count FROM checkin_record
UNION ALL
SELECT 'user_behavior_log', COUNT(*) FROM user_behavior_log;

-- 测试性能建议函数
SELECT * FROM get_performance_recommendations() LIMIT 3; 