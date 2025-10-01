#!/bin/bash

echo "============================================================"
echo "🚀 AI API 完整测试流程"
echo "============================================================"

# 切换到backend目录
cd /Users/yeya/FlutterProjects/ai-time/backend

# 激活虚拟环境
source venv/bin/activate

# 检查端口8000是否被占用
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  端口8000已被占用，尝试关闭..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

# 启动测试服务器
echo ""
echo "1️⃣  启动测试服务器..."
python test_server.py > server.log 2>&1 &
SERVER_PID=$!
echo "   服务器PID: $SERVER_PID"

# 等待服务器启动
echo "   等待服务器启动..."
for i in {1..15}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ 服务器已启动"
        break
    fi
    if [ $i -eq 15 ]; then
        echo "   ❌ 服务器启动超时"
        cat server.log
        kill -9 $SERVER_PID 2>/dev/null
        exit 1
    fi
    sleep 1
    echo -n "."
done

# 运行测试
echo ""
echo "2️⃣  运行API测试..."
python simple_ai_test.py

# 停止服务器
echo ""
echo "3️⃣  停止测试服务器..."
kill -9 $SERVER_PID 2>/dev/null
echo "   ✅ 服务器已停止"

echo ""
echo "============================================================"
echo "✅ 测试完成"
echo "============================================================" 