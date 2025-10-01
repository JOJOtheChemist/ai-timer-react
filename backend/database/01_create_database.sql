-- AI时间管理系统数据库初始化脚本
-- 数据库：ai_time_management
-- 版本：1.0
-- 创建时间：2025-01-01

-- 创建数据库（如果不存在）
CREATE DATABASE ai_time_management 
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'zh_CN.UTF-8'
    LC_CTYPE = 'zh_CN.UTF-8'
    TEMPLATE = template0;

-- 连接到数据库
\c ai_time_management;

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 设置时区
SET timezone = 'Asia/Shanghai'; 