-- ============================================================================
-- AI时间管理系统 - 完整数据库创建脚本
-- 版本：1.0
-- 创建时间：2025-01-01
-- 
-- 使用说明：
-- 1. 确保PostgreSQL版本 >= 12
-- 2. 以超级用户身份执行此脚本
-- 3. 脚本会自动创建数据库、表结构、索引、触发器等
-- ============================================================================

\echo '开始创建AI时间管理系统数据库...'

-- 1. 创建数据库和基础配置
\i 01_create_database.sql

-- 2. 创建用户核心域表结构
\echo '创建用户核心域表结构...'
\i 02_user_core_domain.sql

-- 3. 创建任务与时间表域表结构
\echo '创建任务与时间表域表结构...'
\i 03_task_schedule_domain.sql

-- 4. 创建学习方法与打卡域表结构
\echo '创建学习方法与打卡域表结构...'
\i 04_study_method_domain.sql

-- 5. 创建导师与服务域表结构
\echo '创建导师与服务域表结构...'
\i 05_tutor_service_domain.sql

-- 6. 创建成功案例域表结构
\echo '创建成功案例域表结构...'
\i 06_success_case_domain.sql

-- 7. 创建动态与消息域表结构
\echo '创建动态与消息域表结构...'
\i 07_moment_message_domain.sql

-- 8. 创建AI与统计域表结构
\echo '创建AI与统计域表结构...'
\i 08_ai_statistics_domain.sql

-- 9. 创建徽章域表结构
\echo '创建徽章域表结构...'
\i 09_badge_domain.sql

-- 10. 添加外键约束和完整性检查
\echo '添加外键约束和完整性检查...'
\i 10_foreign_keys_and_constraints.sql

-- 验证数据库创建结果
\echo '验证数据库创建结果...'

-- 检查表数量
SELECT 
    'Tables Created' as check_type,
    COUNT(*) as count,
    'Expected: ~35' as expected
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE';

-- 检查索引数量
SELECT 
    'Indexes Created' as check_type,
    COUNT(*) as count,
    'Expected: ~100+' as expected
FROM pg_indexes 
WHERE schemaname = 'public';

-- 检查触发器数量
SELECT 
    'Triggers Created' as check_type,
    COUNT(*) as count,
    'Expected: ~20+' as expected
FROM information_schema.triggers 
WHERE trigger_schema = 'public';

-- 检查函数数量
SELECT 
    'Functions Created' as check_type,
    COUNT(*) as count,
    'Expected: ~15+' as expected
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_type = 'FUNCTION';

-- 检查视图数量
SELECT 
    'Views Created' as check_type,
    COUNT(*) as count,
    'Expected: ~10+' as expected
FROM information_schema.views 
WHERE table_schema = 'public';

-- 显示所有创建的表
\echo '已创建的表列表：'
SELECT 
    table_name,
    CASE 
        WHEN table_name LIKE '%user%' THEN '用户域'
        WHEN table_name LIKE '%task%' OR table_name LIKE '%time_slot%' OR table_name LIKE '%mood%' THEN '任务时间域'
        WHEN table_name LIKE '%study_method%' OR table_name LIKE '%checkin%' THEN '学习方法域'
        WHEN table_name LIKE '%tutor%' THEN '导师服务域'
        WHEN table_name LIKE '%success_case%' OR table_name LIKE '%case_%' THEN '成功案例域'
        WHEN table_name LIKE '%moment%' OR table_name LIKE '%message%' THEN '动态消息域'
        WHEN table_name LIKE '%ai_%' OR table_name LIKE '%statistic%' OR table_name LIKE '%behavior%' THEN 'AI统计域'
        WHEN table_name LIKE '%badge%' THEN '徽章域'
        ELSE '其他'
    END as domain
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY domain, table_name;

-- 运行数据完整性检查
\echo '运行数据完整性检查...'
SELECT * FROM validate_data_integrity();

-- 获取性能优化建议
\echo '获取性能优化建议...'
SELECT * FROM get_performance_recommendations();

-- 显示系统概览
\echo '系统概览：'
SELECT * FROM v_system_overview;

-- 创建示例数据（可选）
\echo '是否需要创建示例数据？如需要，请运行 sample_data.sql'

-- 最终提示
\echo '============================================================================'
\echo 'AI时间管理系统数据库创建完成！'
\echo ''
\echo '数据库信息：'
\echo '- 数据库名：ai_time_management'
\echo '- 字符编码：UTF8'
\echo '- 时区：Asia/Shanghai'
\echo ''
\echo '核心功能：'
\echo '✓ 用户管理和权限控制'
\echo '✓ 任务和时间表管理'
\echo '✓ 学习方法和打卡系统'
\echo '✓ 导师服务和评价系统'
\echo '✓ 成功案例分享平台'
\echo '✓ 动态广场和消息中心'
\echo '✓ AI分析和智能推荐'
\echo '✓ 徽章系统和成就管理'
\echo '✓ 统计分析和数据可视化'
\echo ''
\echo '维护功能：'
\echo '- 数据完整性检查：SELECT * FROM validate_data_integrity();'
\echo '- 数据修复：SELECT repair_data_integrity();'
\echo '- 性能建议：SELECT * FROM get_performance_recommendations();'
\echo '- 数据库维护：SELECT database_maintenance();'
\echo '- 用户数据备份：SELECT create_user_data_backup(user_id);'
\echo ''
\echo '下一步：'
\echo '1. 配置应用程序连接参数'
\echo '2. 创建应用程序用户和权限'
\echo '3. 导入初始数据（如果需要）'
\echo '4. 配置定时任务（徽章检查、数据清理等）'
\echo '============================================================================' 