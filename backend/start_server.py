#!/usr/bin/env python3
"""
FastAPI 服务器启动脚本
用于测试AI API功能
"""

import uvicorn
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def start_server():
    """启动FastAPI服务器"""
    print("🚀 启动 AI Time Management FastAPI 服务器...")
    print("📍 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("🔧 配置信息:")
    print(f"   - 项目根目录: {project_root}")
    print(f"   - Python路径: {sys.path[0]}")
    print()
    
    try:
        # 启动服务器
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # 开发模式，代码变更自动重载
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        print("请检查:")
        print("1. 数据库连接配置")
        print("2. 依赖包是否安装完整")
        print("3. 端口8000是否被占用")

if __name__ == "__main__":
    start_server() 