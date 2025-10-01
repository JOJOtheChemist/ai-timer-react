#!/usr/bin/env python3
"""
依赖安装脚本
安装AI API测试所需的Python包
"""

import subprocess
import sys
import importlib

def check_and_install_package(package_name, import_name=None):
    """检查并安装Python包"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} 已安装")
        return True
    except ImportError:
        print(f"⚠️  {package_name} 未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✅ {package_name} 安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {package_name} 安装失败: {e}")
            return False

def main():
    """主函数"""
    print("🚀 检查并安装AI API测试依赖")
    print("=" * 40)
    
    # 必需的包列表
    required_packages = [
        ("fastapi", "fastapi"),
        ("uvicorn[standard]", "uvicorn"),
        ("sqlalchemy", "sqlalchemy"),
        ("psycopg2-binary", "psycopg2"),
        ("pydantic", "pydantic"),
        ("pydantic-settings", "pydantic_settings"),
        ("httpx", "httpx"),
        ("python-multipart", "multipart"),
    ]
    
    failed_packages = []
    
    for package_name, import_name in required_packages:
        if not check_and_install_package(package_name, import_name):
            failed_packages.append(package_name)
    
    print("\n" + "=" * 40)
    if failed_packages:
        print(f"❌ 以下包安装失败: {', '.join(failed_packages)}")
        print("请手动安装这些包:")
        for pkg in failed_packages:
            print(f"  pip install {pkg}")
    else:
        print("🎉 所有依赖包安装完成！")
        print("\n下一步:")
        print("1. 确保PostgreSQL服务正在运行")
        print("2. 运行: python init_database.py")
        print("3. 运行: python start_server.py")
        print("4. 运行: python test_ai_apis.py")

if __name__ == "__main__":
    main() 
 