#!/usr/bin/env python3
"""
数据库初始化脚本
创建AI相关的数据库表
"""

import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config import settings
from core.database import engine, Base

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ai_time_management",
    "user": "yeya",
    "password": ""  # 如果有密码请填写
}

def create_database_if_not_exists():
    """创建数据库（如果不存在）"""
    try:
        # 连接到PostgreSQL服务器（不指定数据库）
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (DB_CONFIG["database"],)
        )
        
        if not cursor.fetchone():
            # 创建数据库
            cursor.execute(f'CREATE DATABASE "{DB_CONFIG["database"]}"')
            print(f"✅ 数据库 {DB_CONFIG['database']} 创建成功")
        else:
            print(f"✅ 数据库 {DB_CONFIG['database']} 已存在")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False

def create_ai_tables():
    """创建AI相关的数据库表"""
    
    # AI聊天记录表
    ai_chat_record_sql = """
    CREATE TABLE IF NOT EXISTS ai_chat_record (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        session_id VARCHAR(100) NOT NULL,
        role VARCHAR(20) NOT NULL,
        content TEXT NOT NULL,
        is_analysis SMALLINT DEFAULT 0,
        analysis_tags JSON,
        related_data JSON,
        token_count INTEGER DEFAULT 0,
        create_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_ai_chat_record_user_id ON ai_chat_record(user_id);
    CREATE INDEX IF NOT EXISTS idx_ai_chat_record_session_id ON ai_chat_record(session_id);
    CREATE INDEX IF NOT EXISTS idx_ai_chat_record_create_time ON ai_chat_record(create_time);
    """
    
    # AI分析记录表
    ai_analysis_record_sql = """
    CREATE TABLE IF NOT EXISTS ai_analysis_record (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        analysis_type VARCHAR(20) NOT NULL,
        analysis_tags JSON DEFAULT '[]'::json,
        analysis_content TEXT NOT NULL,
        analysis_data JSON,
        confidence_score DECIMAL(3,2),
        create_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        expire_time TIMESTAMP WITH TIME ZONE
    );
    
    CREATE INDEX IF NOT EXISTS idx_ai_analysis_record_user_id ON ai_analysis_record(user_id);
    CREATE INDEX IF NOT EXISTS idx_ai_analysis_record_type ON ai_analysis_record(analysis_type);
    """
    
    # AI推荐表
    ai_recommendation_sql = """
    CREATE TABLE IF NOT EXISTS ai_recommendation (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        rec_type VARCHAR(20) NOT NULL,
        related_id BIGINT,
        title VARCHAR(200) NOT NULL,
        description TEXT NOT NULL,
        reason TEXT,
        priority INTEGER DEFAULT 1,
        is_accepted SMALLINT DEFAULT 0,
        feedback TEXT,
        create_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        expire_time TIMESTAMP WITH TIME ZONE
    );
    
    CREATE INDEX IF NOT EXISTS idx_ai_recommendation_user_id ON ai_recommendation(user_id);
    CREATE INDEX IF NOT EXISTS idx_ai_recommendation_type ON ai_recommendation(rec_type);
    """
    
    # AI推荐反馈表
    ai_recommendation_feedback_sql = """
    CREATE TABLE IF NOT EXISTS ai_recommendation_feedback (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        method_id BIGINT NOT NULL,
        feedback_type VARCHAR(20) NOT NULL,
        rating INTEGER,
        comment TEXT,
        create_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_ai_feedback_user_id ON ai_recommendation_feedback(user_id);
    CREATE INDEX IF NOT EXISTS idx_ai_feedback_method_id ON ai_recommendation_feedback(method_id);
    """
    
    # 学习方法表（如果不存在）
    study_methods_sql = """
    CREATE TABLE IF NOT EXISTS study_methods (
        id BIGSERIAL PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        category VARCHAR(100) NOT NULL,
        description TEXT NOT NULL,
        difficulty_level VARCHAR(20) DEFAULT 'beginner',
        estimated_time INTEGER DEFAULT 30,
        tags JSON DEFAULT '[]'::json,
        checkin_count INTEGER DEFAULT 0,
        is_active BOOLEAN DEFAULT true,
        create_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        update_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_study_methods_category ON study_methods(category);
    CREATE INDEX IF NOT EXISTS idx_study_methods_active ON study_methods(is_active);
    """
    
    # 方法打卡表（如果不存在）
    method_checkins_sql = """
    CREATE TABLE IF NOT EXISTS method_checkins (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        method_id BIGINT NOT NULL,
        checkin_date DATE NOT NULL,
        progress INTEGER DEFAULT 0,
        notes TEXT,
        create_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_method_checkins_user_id ON method_checkins(user_id);
    CREATE INDEX IF NOT EXISTS idx_method_checkins_method_id ON method_checkins(method_id);
    CREATE INDEX IF NOT EXISTS idx_method_checkins_date ON method_checkins(checkin_date);
    """
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 执行创建表的SQL
        tables = [
            ("ai_chat_record", ai_chat_record_sql),
            ("ai_analysis_record", ai_analysis_record_sql),
            ("ai_recommendation", ai_recommendation_sql),
            ("ai_recommendation_feedback", ai_recommendation_feedback_sql),
            ("study_methods", study_methods_sql),
            ("method_checkins", method_checkins_sql),
        ]
        
        for table_name, sql in tables:
            try:
                cursor.execute(sql)
                print(f"✅ 表 {table_name} 创建/更新成功")
            except Exception as e:
                print(f"❌ 创建表 {table_name} 失败: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 创建AI表失败: {e}")
        return False

def insert_sample_data():
    """插入示例数据"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 插入示例学习方法
        sample_methods = [
            ("艾宾浩斯记忆法", "记忆法", "基于遗忘曲线的科学记忆方法，通过合理安排复习时间提高记忆效率", "intermediate", 45),
            ("番茄工作法", "时间管理", "将工作分解为25分钟的专注时段，中间休息5分钟", "beginner", 30),
            ("费曼学习法", "理解法", "通过教授他人来检验和加深自己的理解", "advanced", 60),
            ("思维导图", "整理法", "用图形化方式整理和记忆知识点", "beginner", 30),
            ("间隔重复", "记忆法", "根据遗忘规律安排复习间隔，提高长期记忆效果", "intermediate", 40),
        ]
        
        for name, category, description, difficulty, time in sample_methods:
            cursor.execute("""
                INSERT INTO study_methods (name, category, description, difficulty_level, estimated_time)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (name, category, description, difficulty, time))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ 示例数据插入成功")
        return True
        
    except Exception as e:
        print(f"❌ 插入示例数据失败: {e}")
        return False

def check_tables():
    """检查表是否创建成功"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        tables_to_check = [
            "ai_chat_record",
            "ai_analysis_record", 
            "ai_recommendation",
            "ai_recommendation_feedback",
            "study_methods",
            "method_checkins"
        ]
        
        print("\n🔍 检查数据库表状态:")
        for table in tables_to_check:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table,))
            
            exists = cursor.fetchone()[0]
            if exists:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: 存在，记录数: {count}")
            else:
                print(f"❌ {table}: 不存在")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查表状态失败: {e}")

def main():
    """主函数"""
    print("🚀 AI Time Management 数据库初始化")
    print("=" * 50)
    
    # 1. 创建数据库
    if not create_database_if_not_exists():
        print("❌ 数据库创建失败，退出")
        return
    
    # 2. 创建表
    if not create_ai_tables():
        print("❌ 创建表失败，退出")
        return
    
    # 3. 插入示例数据
    if not insert_sample_data():
        print("⚠️  插入示例数据失败，但可以继续")
    
    # 4. 检查表状态
    check_tables()
    
    print("\n🎉 数据库初始化完成！")
    print("现在可以运行以下命令测试API:")
    print("1. python start_server.py  # 启动服务器")
    print("2. python test_ai_apis.py  # 测试API")

if __name__ == "__main__":
    main() 