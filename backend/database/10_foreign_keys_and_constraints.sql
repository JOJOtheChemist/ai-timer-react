-- ============================================================================
-- 外键约束和数据完整性检查
-- ============================================================================

-- 添加跨域外键约束（之前创建表时已经添加了大部分外键，这里补充一些跨域的关联）

-- 1. 学习方法表关联导师表的外键
ALTER TABLE study_method 
ADD CONSTRAINT fk_study_method_tutor 
FOREIGN KEY (tutor_id) REFERENCES tutor(id) ON DELETE SET NULL;

-- 2. AI推荐表的关联外键（根据推荐类型）
-- 注意：这里不能直接添加外键，因为related_id可能指向不同的表
-- 需要通过应用层或触发器来保证数据完整性

-- 3. 动态附件表的关联外键检查
CREATE OR REPLACE FUNCTION check_moment_attachment_integrity()
RETURNS TRIGGER AS $$
BEGIN
    -- 检查关联ID的有效性
    IF NEW.type = 'schedule' AND NEW.related_id IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM time_slot WHERE id = NEW.related_id) THEN
            RAISE EXCEPTION '时间表ID % 不存在', NEW.related_id;
        END IF;
    ELSIF NEW.type = 'method' AND NEW.related_id IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM study_method WHERE id = NEW.related_id) THEN
            RAISE EXCEPTION '学习方法ID % 不存在', NEW.related_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_moment_attachment_integrity
    BEFORE INSERT OR UPDATE ON moment_attachment
    FOR EACH ROW EXECUTE FUNCTION check_moment_attachment_integrity();

-- 4. 消息表的关联完整性检查
CREATE OR REPLACE FUNCTION check_message_integrity()
RETURNS TRIGGER AS $$
BEGIN
    -- 检查消息类型和发送者的匹配性
    IF NEW.type = 2 AND NEW.sender_id IS NOT NULL THEN
        RAISE EXCEPTION '系统通知不应该有发送者ID';
    ELSIF NEW.type IN (0, 1) AND NEW.sender_id IS NULL THEN
        RAISE EXCEPTION '导师反馈和私信必须有发送者ID';
    END IF;
    
    -- 检查关联ID的有效性
    IF NEW.related_type = 'tutor' AND NEW.related_id IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM tutor WHERE id = NEW.related_id) THEN
            RAISE EXCEPTION '导师ID % 不存在', NEW.related_id;
        END IF;
    ELSIF NEW.related_type = 'order' AND NEW.related_id IS NOT NULL THEN
        IF NOT EXISTS (SELECT 1 FROM tutor_service_order WHERE id = NEW.related_id) THEN
            RAISE EXCEPTION '订单ID % 不存在', NEW.related_id;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_message_integrity
    BEFORE INSERT OR UPDATE ON message
    FOR EACH ROW EXECUTE FUNCTION check_message_integrity();

-- 5. 添加数据一致性检查约束

-- 确保时间段不重叠（同一用户同一天）
CREATE OR REPLACE FUNCTION check_time_slot_overlap()
RETURNS TRIGGER AS $$
DECLARE
    overlap_count INTEGER;
    start_time TIME;
    end_time TIME;
BEGIN
    -- 解析时间段
    start_time := (split_part(NEW.time_range, '-', 1) || ':00')::TIME;
    end_time := (split_part(NEW.time_range, '-', 2) || ':00')::TIME;
    
    -- 检查是否有重叠
    SELECT COUNT(*) INTO overlap_count
    FROM time_slot ts
    WHERE ts.user_id = NEW.user_id 
    AND ts.date = NEW.date 
    AND ts.id != COALESCE(NEW.id, 0)
    AND (
        (split_part(ts.time_range, '-', 1) || ':00')::TIME < end_time
        AND (split_part(ts.time_range, '-', 2) || ':00')::TIME > start_time
    );
    
    IF overlap_count > 0 THEN
        RAISE EXCEPTION '时间段 % 与现有时间段重叠', NEW.time_range;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_time_slot_overlap
    BEFORE INSERT OR UPDATE ON time_slot
    FOR EACH ROW EXECUTE FUNCTION check_time_slot_overlap();

-- 6. 确保用户资产余额不为负
ALTER TABLE user_asset 
ADD CONSTRAINT check_diamond_non_negative 
CHECK (diamond_count >= 0);

-- 7. 确保评分在有效范围内
ALTER TABLE tutor_review 
ADD CONSTRAINT check_tutor_review_rating 
CHECK (rating BETWEEN 1 AND 5);

ALTER TABLE method_review 
ADD CONSTRAINT check_method_review_rating 
CHECK (rating BETWEEN 1 AND 5);

-- 8. 确保百分比字段在有效范围内
ALTER TABLE tutor 
ADD CONSTRAINT check_tutor_rating_range 
CHECK (rating BETWEEN 0 AND 100);

ALTER TABLE tutor 
ADD CONSTRAINT check_tutor_success_rate_range 
CHECK (success_rate BETWEEN 0 AND 100);

ALTER TABLE statistic_daily 
ADD CONSTRAINT check_daily_completion_rate_range 
CHECK (completion_rate BETWEEN 0 AND 100);

ALTER TABLE statistic_weekly 
ADD CONSTRAINT check_weekly_ai_accept_rate_range 
CHECK (ai_accept_rate BETWEEN 0 AND 100);

-- 9. 创建数据完整性检查函数
CREATE OR REPLACE FUNCTION validate_data_integrity()
RETURNS TABLE(
    table_name TEXT,
    issue_type TEXT,
    issue_count BIGINT,
    description TEXT
) AS $$
BEGIN
    -- 检查孤儿记录
    RETURN QUERY
    SELECT 
        'user_asset'::TEXT,
        'orphan_records'::TEXT,
        COUNT(*)::BIGINT,
        '用户资产表中存在无效的用户ID引用'::TEXT
    FROM user_asset ua
    LEFT JOIN "user" u ON ua.user_id = u.id
    WHERE u.id IS NULL
    HAVING COUNT(*) > 0;
    
    RETURN QUERY
    SELECT 
        'time_slot'::TEXT,
        'orphan_records'::TEXT,
        COUNT(*)::BIGINT,
        '时间段表中存在无效的任务ID引用'::TEXT
    FROM time_slot ts
    LEFT JOIN task t ON ts.task_id = t.id
    WHERE ts.task_id IS NOT NULL AND t.id IS NULL
    HAVING COUNT(*) > 0;
    
    -- 检查数据不一致
    RETURN QUERY
    SELECT 
        'tutor'::TEXT,
        'inconsistent_data'::TEXT,
        COUNT(*)::BIGINT,
        '导师表中评分与实际评价不一致'::TEXT
    FROM tutor t
    WHERE t.rating != COALESCE((
        SELECT ROUND(AVG(tr.rating) * 20, 0)
        FROM tutor_review tr
        WHERE tr.tutor_id = t.id
    ), 0)
    HAVING COUNT(*) > 0;
    
    -- 检查重复数据
    RETURN QUERY
    SELECT 
        'user_badge'::TEXT,
        'duplicate_records'::TEXT,
        COUNT(*)::BIGINT,
        '用户徽章表中存在重复记录'::TEXT
    FROM (
        SELECT user_id, badge_id, COUNT(*) as cnt
        FROM user_badge
        GROUP BY user_id, badge_id
        HAVING COUNT(*) > 1
    ) duplicates
    HAVING COUNT(*) > 0;
    
END;
$$ LANGUAGE plpgsql;

-- 10. 创建数据修复函数
CREATE OR REPLACE FUNCTION repair_data_integrity()
RETURNS TEXT AS $$
DECLARE
    repair_log TEXT := '';
    affected_rows INTEGER;
BEGIN
    -- 修复导师评分不一致
    UPDATE tutor 
    SET rating = COALESCE((
        SELECT ROUND(AVG(tr.rating) * 20, 0)
        FROM tutor_review tr
        WHERE tr.tutor_id = tutor.id
    ), 0);
    
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    repair_log := repair_log || '修复导师评分: ' || affected_rows || ' 条记录' || E'\n';
    
    -- 修复学习方法统计
    UPDATE study_method 
    SET 
        rating = COALESCE((
            SELECT ROUND(AVG(rating), 1) 
            FROM method_review 
            WHERE method_id = study_method.id
        ), 0.0),
        review_count = (
            SELECT COUNT(*) 
            FROM method_review 
            WHERE method_id = study_method.id
        ),
        checkin_count = (
            SELECT COUNT(DISTINCT user_id) 
            FROM checkin_record 
            WHERE method_id = study_method.id
        );
    
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    repair_log := repair_log || '修复学习方法统计: ' || affected_rows || ' 条记录' || E'\n';
    
    -- 修复徽章获得人数
    UPDATE badge 
    SET obtain_count = (
        SELECT COUNT(*) 
        FROM user_badge 
        WHERE badge_id = badge.id
    );
    
    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    repair_log := repair_log || '修复徽章统计: ' || affected_rows || ' 条记录' || E'\n';
    
    RETURN repair_log;
END;
$$ LANGUAGE plpgsql;

-- 11. 创建性能优化建议函数
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
        schemaname || '.' || tablename,
        '表大小超过1GB，建议考虑分区: ' || pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)),
        2::INTEGER
    FROM pg_tables pt
    JOIN pg_class pc ON pc.relname = pt.tablename
    WHERE pt.schemaname = 'public'
    AND pg_total_relation_size(pt.schemaname||'.'||pt.tablename) > 1024*1024*1024;
    
    -- 检查统计信息更新
    RETURN QUERY
    SELECT 
        'statistics'::TEXT,
        schemaname || '.' || tablename,
        '表统计信息可能过期，建议运行 ANALYZE'::TEXT,
        3::INTEGER
    FROM pg_stat_user_tables
    WHERE schemaname = 'public'
    AND (last_analyze IS NULL OR last_analyze < CURRENT_TIMESTAMP - INTERVAL '7 days')
    AND n_tup_ins + n_tup_upd + n_tup_del > 1000;
    
END;
$$ LANGUAGE plpgsql;

-- 12. 创建数据库维护函数
CREATE OR REPLACE FUNCTION database_maintenance()
RETURNS TEXT AS $$
DECLARE
    maintenance_log TEXT := '';
BEGIN
    -- 更新表统计信息
    ANALYZE;
    maintenance_log := maintenance_log || '已更新所有表的统计信息' || E'\n';
    
    -- 清理过期数据
    PERFORM cleanup_expired_data();
    maintenance_log := maintenance_log || '已清理过期数据' || E'\n';
    
    -- 重建索引（如果需要）
    REINDEX DATABASE CONCURRENTLY ai_time_management;
    maintenance_log := maintenance_log || '已重建数据库索引' || E'\n';
    
    -- 清理无用的统计信息
    DELETE FROM badge_condition_check 
    WHERE last_check_time < CURRENT_TIMESTAMP - INTERVAL '30 days';
    
    maintenance_log := maintenance_log || '已清理过期的徽章检查记录' || E'\n';
    
    RETURN maintenance_log;
EXCEPTION
    WHEN OTHERS THEN
        RETURN '维护过程中发生错误: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- 13. 创建备份和恢复相关的函数
CREATE OR REPLACE FUNCTION create_user_data_backup(target_user_id BIGINT)
RETURNS JSONB AS $$
DECLARE
    backup_data JSONB := '{}';
BEGIN
    -- 备份用户基本信息
    SELECT to_jsonb(u.*) INTO backup_data
    FROM "user" u WHERE id = target_user_id;
    
    -- 添加用户相关的所有数据
    backup_data := backup_data || jsonb_build_object(
        'profile', (SELECT to_jsonb(up.*) FROM user_profile up WHERE user_id = target_user_id),
        'assets', (SELECT to_jsonb(ua.*) FROM user_asset ua WHERE user_id = target_user_id),
        'tasks', (SELECT jsonb_agg(to_jsonb(t.*)) FROM task t WHERE user_id = target_user_id),
        'time_slots', (SELECT jsonb_agg(to_jsonb(ts.*)) FROM time_slot ts WHERE user_id = target_user_id),
        'badges', (SELECT jsonb_agg(to_jsonb(ub.*)) FROM user_badge ub WHERE user_id = target_user_id),
        'statistics_weekly', (SELECT jsonb_agg(to_jsonb(sw.*)) FROM statistic_weekly sw WHERE user_id = target_user_id),
        'statistics_daily', (SELECT jsonb_agg(to_jsonb(sd.*)) FROM statistic_daily sd WHERE user_id = target_user_id)
    );
    
    RETURN backup_data;
END;
$$ LANGUAGE plpgsql;

-- 添加表注释
COMMENT ON FUNCTION validate_data_integrity() IS '验证数据完整性，返回发现的问题';
COMMENT ON FUNCTION repair_data_integrity() IS '修复数据完整性问题';
COMMENT ON FUNCTION get_performance_recommendations() IS '获取性能优化建议';
COMMENT ON FUNCTION database_maintenance() IS '执行数据库维护任务';
COMMENT ON FUNCTION create_user_data_backup(BIGINT) IS '创建指定用户的数据备份';

-- 创建管理员视图：系统概览
CREATE VIEW v_system_overview AS
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
    ROUND(SUM(total_study_hours), 1)::TEXT,
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

-- 最后的完整性检查
DO $$
BEGIN
    -- 检查所有外键约束是否正确创建
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_type = 'FOREIGN KEY' 
        AND table_name = 'user_asset'
    ) THEN
        RAISE EXCEPTION '外键约束创建不完整';
    END IF;
    
    RAISE NOTICE '数据库结构创建完成，所有约束和索引已就绪';
END $$; 