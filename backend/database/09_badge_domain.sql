-- ============================================================================
-- 八、徽章域（支撑个人主页徽章墙）
-- ============================================================================

-- 1. 徽章表
CREATE TABLE badge (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE, -- 徽章名称
    icon VARCHAR(20) NOT NULL, -- 图标，如"🔥"
    description VARCHAR(200) NOT NULL, -- 徽章描述
    condition_text TEXT NOT NULL, -- 解锁条件描述
    condition_config JSONB NOT NULL, -- 解锁条件配置（JSON格式）
    category VARCHAR(20) DEFAULT 'general' CHECK (category IN ('general', 'study', 'social', 'achievement', 'special')), -- 徽章分类
    rarity SMALLINT DEFAULT 1 CHECK (rarity BETWEEN 1 AND 5), -- 稀有度1-5
    sort_order INTEGER DEFAULT 0, -- 排序序号
    is_active SMALLINT DEFAULT 1 CHECK (is_active IN (0, 1)), -- 是否启用
    obtain_count INTEGER DEFAULT 0 CHECK (obtain_count >= 0), -- 获得人数
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. 用户徽章表
CREATE TABLE user_badge (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    badge_id BIGINT NOT NULL,
    obtain_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- 获得时间
    progress_data JSONB DEFAULT NULL, -- 进度数据（用于部分完成的徽章）
    is_displayed SMALLINT DEFAULT 1 CHECK (is_displayed IN (0, 1)), -- 是否在个人主页显示
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badge(id) ON DELETE CASCADE,
    UNIQUE (user_id, badge_id) -- 避免重复获得同一徽章
);

-- 3. 徽章获得日志表
CREATE TABLE badge_obtain_log (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    badge_id BIGINT NOT NULL,
    trigger_action VARCHAR(50) NOT NULL, -- 触发动作
    trigger_data JSONB DEFAULT NULL, -- 触发数据
    obtain_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badge(id) ON DELETE CASCADE
);

-- 4. 徽章条件检查表（用于缓存检查结果）
CREATE TABLE badge_condition_check (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    badge_id BIGINT NOT NULL,
    current_progress JSONB DEFAULT NULL, -- 当前进度
    is_qualified SMALLINT DEFAULT 0 CHECK (is_qualified IN (0, 1)), -- 是否符合条件
    last_check_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badge(id) ON DELETE CASCADE,
    UNIQUE (user_id, badge_id)
);

-- 创建索引
CREATE INDEX idx_badge_category ON badge(category);
CREATE INDEX idx_badge_rarity ON badge(rarity);
CREATE INDEX idx_badge_is_active ON badge(is_active);
CREATE INDEX idx_badge_sort_order ON badge(sort_order);
CREATE INDEX idx_badge_obtain_count ON badge(obtain_count);

CREATE INDEX idx_user_badge_user_id ON user_badge(user_id);
CREATE INDEX idx_user_badge_badge_id ON user_badge(badge_id);
CREATE INDEX idx_user_badge_obtain_time ON user_badge(obtain_time);
CREATE INDEX idx_user_badge_is_displayed ON user_badge(is_displayed);

CREATE INDEX idx_badge_obtain_log_user_id ON badge_obtain_log(user_id);
CREATE INDEX idx_badge_obtain_log_badge_id ON badge_obtain_log(badge_id);
CREATE INDEX idx_badge_obtain_log_trigger_action ON badge_obtain_log(trigger_action);
CREATE INDEX idx_badge_obtain_log_obtain_time ON badge_obtain_log(obtain_time);

CREATE INDEX idx_badge_condition_check_user_id ON badge_condition_check(user_id);
CREATE INDEX idx_badge_condition_check_badge_id ON badge_condition_check(badge_id);
CREATE INDEX idx_badge_condition_check_is_qualified ON badge_condition_check(is_qualified);
CREATE INDEX idx_badge_condition_check_last_check_time ON badge_condition_check(last_check_time);

-- 添加 GIN 索引支持 JSONB 查询
CREATE INDEX idx_badge_condition_config_gin ON badge USING GIN (condition_config);
CREATE INDEX idx_user_badge_progress_data_gin ON user_badge USING GIN (progress_data);
CREATE INDEX idx_badge_obtain_log_trigger_data_gin ON badge_obtain_log USING GIN (trigger_data);
CREATE INDEX idx_badge_condition_check_progress_gin ON badge_condition_check USING GIN (current_progress);

-- 为相关表添加更新时间触发器
CREATE TRIGGER update_badge_update_time BEFORE UPDATE ON badge 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建函数用于检查徽章条件
CREATE OR REPLACE FUNCTION check_badge_conditions(target_user_id BIGINT, target_badge_id BIGINT DEFAULT NULL)
RETURNS VOID AS $$
DECLARE
    badge_record RECORD;
    user_stats RECORD;
    is_qualified BOOLEAN;
    progress_data JSONB;
BEGIN
    -- 如果指定了徽章ID，只检查该徽章；否则检查所有启用的徽章
    FOR badge_record IN 
        SELECT * FROM badge 
        WHERE is_active = 1 
        AND (target_badge_id IS NULL OR id = target_badge_id)
        AND id NOT IN (SELECT badge_id FROM user_badge WHERE user_id = target_user_id)
    LOOP
        is_qualified := FALSE;
        progress_data := '{}'::jsonb;
        
        -- 根据徽章类型检查条件
        CASE badge_record.condition_config->>'type'
            WHEN 'consecutive_checkin' THEN
                -- 连续打卡徽章
                SELECT COUNT(*) >= (badge_record.condition_config->>'days')::INTEGER
                INTO is_qualified
                FROM checkin_record cr
                WHERE cr.user_id = target_user_id
                AND cr.checkin_time >= CURRENT_DATE - INTERVAL '1 day' * (badge_record.condition_config->>'days')::INTEGER
                AND DATE(cr.checkin_time) = CURRENT_DATE - INTERVAL '1 day' * (ROW_NUMBER() OVER (ORDER BY cr.checkin_time DESC) - 1);
                
            WHEN 'total_study_hours' THEN
                -- 总学习时长徽章
                SELECT up.total_study_hours >= (badge_record.condition_config->>'hours')::DECIMAL
                INTO is_qualified
                FROM user_profile up
                WHERE up.user_id = target_user_id;
                
            WHEN 'weekly_hours_exceed' THEN
                -- 周时长超标徽章
                SELECT COUNT(*) >= (badge_record.condition_config->>'weeks')::INTEGER
                INTO is_qualified
                FROM statistic_weekly sw
                WHERE sw.user_id = target_user_id
                AND sw.total_study_hours >= (badge_record.condition_config->>'target_hours')::DECIMAL;
                
            WHEN 'share_moments' THEN
                -- 分享动态徽章
                SELECT COUNT(*) >= (badge_record.condition_config->>'count')::INTEGER
                INTO is_qualified
                FROM moment m
                WHERE m.user_id = target_user_id
                AND m.status = 0;
                
            WHEN 'diamond_recharge' THEN
                -- 首次充值徽章
                SELECT ua.diamond_count > 0
                INTO is_qualified
                FROM user_asset ua
                WHERE ua.user_id = target_user_id;
                
            WHEN 'completion_rate' THEN
                -- 完成率徽章
                SELECT COUNT(*) >= (badge_record.condition_config->>'days')::INTEGER
                INTO is_qualified
                FROM statistic_daily sd
                WHERE sd.user_id = target_user_id
                AND sd.completion_rate >= (badge_record.condition_config->>'rate')::DECIMAL
                AND sd.date >= CURRENT_DATE - INTERVAL '1 month';
                
            ELSE
                -- 默认情况，不符合条件
                is_qualified := FALSE;
        END CASE;
        
        -- 更新或插入条件检查结果
        INSERT INTO badge_condition_check (user_id, badge_id, current_progress, is_qualified)
        VALUES (target_user_id, badge_record.id, progress_data, CASE WHEN is_qualified THEN 1 ELSE 0 END)
        ON CONFLICT (user_id, badge_id)
        DO UPDATE SET
            current_progress = EXCLUDED.current_progress,
            is_qualified = EXCLUDED.is_qualified,
            last_check_time = CURRENT_TIMESTAMP;
        
        -- 如果符合条件，自动颁发徽章
        IF is_qualified THEN
            INSERT INTO user_badge (user_id, badge_id, progress_data)
            VALUES (target_user_id, badge_record.id, progress_data)
            ON CONFLICT (user_id, badge_id) DO NOTHING;
            
            -- 记录获得日志
            INSERT INTO badge_obtain_log (user_id, badge_id, trigger_action, trigger_data)
            VALUES (target_user_id, badge_record.id, 'auto_check', progress_data);
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 创建函数用于更新徽章统计
CREATE OR REPLACE FUNCTION update_badge_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- 更新徽章获得人数
    IF TG_OP = 'INSERT' AND TG_TABLE_NAME = 'user_badge' THEN
        UPDATE badge 
        SET obtain_count = (
            SELECT COUNT(*) 
            FROM user_badge 
            WHERE badge_id = NEW.badge_id
        )
        WHERE id = NEW.badge_id;
    ELSIF TG_OP = 'DELETE' AND TG_TABLE_NAME = 'user_badge' THEN
        UPDATE badge 
        SET obtain_count = (
            SELECT COUNT(*) 
            FROM user_badge 
            WHERE badge_id = OLD.badge_id
        )
        WHERE id = OLD.badge_id;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- 创建触发器自动更新徽章统计
CREATE TRIGGER trigger_update_badge_stats 
    AFTER INSERT OR DELETE ON user_badge
    FOR EACH ROW EXECUTE FUNCTION update_badge_stats();

-- 创建函数用于自动检查徽章条件（在相关操作后触发）
CREATE OR REPLACE FUNCTION auto_check_badges()
RETURNS TRIGGER AS $$
BEGIN
    -- 根据不同的触发表执行相应的徽章检查
    IF TG_TABLE_NAME = 'checkin_record' THEN
        -- 打卡相关徽章检查
        PERFORM check_badge_conditions(NEW.user_id);
    ELSIF TG_TABLE_NAME = 'moment' THEN
        -- 动态相关徽章检查
        PERFORM check_badge_conditions(NEW.user_id);
    ELSIF TG_TABLE_NAME = 'user_asset' THEN
        -- 资产相关徽章检查
        PERFORM check_badge_conditions(NEW.user_id);
    ELSIF TG_TABLE_NAME = 'statistic_weekly' THEN
        -- 周统计相关徽章检查
        PERFORM check_badge_conditions(NEW.user_id);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器在相关操作后自动检查徽章
CREATE TRIGGER trigger_auto_check_badges_checkin 
    AFTER INSERT ON checkin_record
    FOR EACH ROW EXECUTE FUNCTION auto_check_badges();

CREATE TRIGGER trigger_auto_check_badges_moment 
    AFTER INSERT ON moment
    FOR EACH ROW EXECUTE FUNCTION auto_check_badges();

CREATE TRIGGER trigger_auto_check_badges_asset 
    AFTER UPDATE ON user_asset
    FOR EACH ROW EXECUTE FUNCTION auto_check_badges();

CREATE TRIGGER trigger_auto_check_badges_weekly 
    AFTER INSERT OR UPDATE ON statistic_weekly
    FOR EACH ROW EXECUTE FUNCTION auto_check_badges();

-- 添加表注释
COMMENT ON TABLE badge IS '徽章表';
COMMENT ON TABLE user_badge IS '用户徽章表';
COMMENT ON TABLE badge_obtain_log IS '徽章获得日志表';
COMMENT ON TABLE badge_condition_check IS '徽章条件检查表';

-- 添加字段注释
COMMENT ON COLUMN badge.category IS '徽章分类：general-通用，study-学习，social-社交，achievement-成就，special-特殊';
COMMENT ON COLUMN badge.rarity IS '稀有度：1-5，数字越大越稀有';
COMMENT ON COLUMN badge.condition_config IS '解锁条件配置，JSON格式';
COMMENT ON COLUMN badge.obtain_count IS '获得该徽章的用户数量';

COMMENT ON COLUMN user_badge.progress_data IS '进度数据，用于记录获得徽章时的相关数据';
COMMENT ON COLUMN user_badge.is_displayed IS '是否在个人主页显示：0-否，1-是';

COMMENT ON COLUMN badge_obtain_log.trigger_action IS '触发动作，如checkin、share_moment等';
COMMENT ON COLUMN badge_obtain_log.trigger_data IS '触发时的相关数据';

COMMENT ON COLUMN badge_condition_check.current_progress IS '当前进度数据';
COMMENT ON COLUMN badge_condition_check.is_qualified IS '是否符合获得条件：0-否，1-是';

-- 创建复合索引优化常用查询
CREATE INDEX idx_badge_category_rarity_order ON badge(category, rarity, sort_order);
CREATE INDEX idx_user_badge_user_displayed_time ON user_badge(user_id, is_displayed, obtain_time DESC);
CREATE INDEX idx_badge_condition_check_user_qualified ON badge_condition_check(user_id, is_qualified);

-- 创建视图：用户徽章概览
CREATE VIEW v_user_badge_overview AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(ub.id) as total_badges,
    COUNT(CASE WHEN b.rarity >= 4 THEN 1 END) as rare_badges,
    COUNT(CASE WHEN ub.is_displayed = 1 THEN 1 END) as displayed_badges,
    MAX(ub.obtain_time) as latest_badge_time
FROM "user" u
LEFT JOIN user_badge ub ON u.id = ub.user_id
LEFT JOIN badge b ON ub.badge_id = b.id
GROUP BY u.id, u.username
ORDER BY total_badges DESC;

-- 创建视图：徽章稀有度统计
CREATE VIEW v_badge_rarity_stats AS
SELECT 
    b.rarity,
    COUNT(*) as total_badges,
    AVG(b.obtain_count) as avg_obtain_count,
    MIN(b.obtain_count) as min_obtain_count,
    MAX(b.obtain_count) as max_obtain_count
FROM badge b
WHERE b.is_active = 1
GROUP BY b.rarity
ORDER BY b.rarity DESC;

-- 插入默认徽章数据
INSERT INTO badge (name, icon, description, condition_text, condition_config, category, rarity, sort_order) VALUES
('坚持之星', '🔥', '连续7天完成学习计划打卡', '连续7天打卡', '{"type":"consecutive_checkin","days":7}', 'study', 2, 1),
('复习王者', '📚', '连续14天完成复习任务，复习频率达到80%以上', '连续14天高频复习', '{"type":"consecutive_checkin","days":14}', 'study', 3, 2),
('目标达成', '🎯', '单周学习时长超过计划时长的120%', '周时长超标120%', '{"type":"weekly_hours_exceed","target_hours":40,"weeks":1}', 'achievement', 2, 3),
('分享达人', '👥', '累计发布5条学习动态，获得20次以上点赞', '发布5条动态', '{"type":"share_moments","count":5}', 'social', 2, 4),
('首次充值', '💎', '完成首次钻石充值，开启导师指导服务', '完成首次充值', '{"type":"diamond_recharge"}', 'general', 1, 5),
('进步神速', '📈', '单周学习时长较上一周增长50%以上', '周时长增长50%', '{"type":"weekly_improvement","rate":50}', 'achievement', 3, 6),
('上岸先锋', '🎓', '成功上传考研上岸经验案例，通过官方审核', '上传上岸案例', '{"type":"upload_success_case"}', 'special', 5, 7),
('学霸认证', '🏅', '累计学习时长达到3000小时，且周均打卡率90%以上', '总时长3000小时', '{"type":"total_study_hours","hours":3000}', 'achievement', 5, 8);

-- 创建定时任务函数（需要配合 pg_cron 扩展使用）
CREATE OR REPLACE FUNCTION daily_badge_check()
RETURNS VOID AS $$
BEGIN
    -- 每日检查所有用户的徽章条件
    PERFORM check_badge_conditions(u.id)
    FROM "user" u
    WHERE u.status = 0;
    
    -- 清理过期的条件检查记录（超过30天）
    DELETE FROM badge_condition_check 
    WHERE last_check_time < CURRENT_TIMESTAMP - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql; 