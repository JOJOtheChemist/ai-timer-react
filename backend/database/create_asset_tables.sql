-- ============================================================================
-- 用户资产系统补充表
-- 为用户资产管理API添加缺失的数据库表
-- ============================================================================

-- 1. 创建资产变动记录表
CREATE TABLE IF NOT EXISTS user_asset_record (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    record_type VARCHAR(20) NOT NULL CHECK (record_type IN ('recharge', 'consume', 'reward')),
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    description VARCHAR(200),
    related_type VARCHAR(20),
    related_id BIGINT,
    order_id VARCHAR(100),
    payment_method VARCHAR(20),
    create_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_asset_record_user FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 2. 创建充值订单表
CREATE TABLE IF NOT EXISTS recharge_order (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    diamond_count INTEGER NOT NULL CHECK (diamond_count > 0),
    payment_method VARCHAR(20) DEFAULT 'alipay',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'expired')),
    expire_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_recharge_order_user FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- 3. 为 user_asset 表添加缺失字段（如果不存在）
DO $$ 
BEGIN
    -- 添加 total_recharge 字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_asset' AND column_name = 'total_recharge'
    ) THEN
        ALTER TABLE user_asset ADD COLUMN total_recharge DECIMAL(10,2) DEFAULT 0.00;
    END IF;
    
    -- 添加 total_consume 字段
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_asset' AND column_name = 'total_consume'
    ) THEN
        ALTER TABLE user_asset ADD COLUMN total_consume INTEGER DEFAULT 0;
    END IF;
END $$;

-- 4. 创建索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_user_asset_record_user_id ON user_asset_record(user_id);
CREATE INDEX IF NOT EXISTS idx_user_asset_record_type ON user_asset_record(record_type);
CREATE INDEX IF NOT EXISTS idx_user_asset_record_time ON user_asset_record(create_time DESC);
CREATE INDEX IF NOT EXISTS idx_recharge_order_user_id ON recharge_order(user_id);
CREATE INDEX IF NOT EXISTS idx_recharge_order_status ON recharge_order(status);
CREATE INDEX IF NOT EXISTS idx_recharge_order_time ON recharge_order(created_at DESC);

-- 5. 创建触发器：自动更新 recharge_order 的 updated_at 字段
CREATE OR REPLACE FUNCTION update_recharge_order_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_recharge_order_updated_at
    BEFORE UPDATE ON recharge_order
    FOR EACH ROW
    EXECUTE FUNCTION update_recharge_order_updated_at();

-- 6. 添加注释
COMMENT ON TABLE user_asset_record IS '用户资产变动记录表';
COMMENT ON TABLE recharge_order IS '用户充值订单表';
COMMENT ON COLUMN user_asset.total_recharge IS '用户总充值金额（元）';
COMMENT ON COLUMN user_asset.total_consume IS '用户总消费钻石数';

-- 完成
SELECT 'User asset tables created successfully!' AS status; 