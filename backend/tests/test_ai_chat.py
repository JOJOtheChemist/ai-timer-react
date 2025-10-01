import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

from main import app
from core.database import get_db, Base
from models.schemas.ai import ChatMessageCreate

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    # 创建测试表
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # 清理测试表
    Base.metadata.drop_all(bind=engine)

class TestAIChat:
    """AI聊天功能测试"""
    
    def test_send_chat_message(self, client):
        """测试发送聊天消息"""
        message_data = {
            "content": "你好，我想了解时间管理的方法",
            "session_id": None
        }
        
        response = client.post(
            "/api/v1/ai/chat?user_id=1",
            json=message_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "session_id" in data
        assert data["token_count"] > 0
    
    def test_get_chat_history(self, client):
        """测试获取聊天历史"""
        # 先发送一条消息
        message_data = {
            "content": "测试消息",
            "session_id": None
        }
        client.post("/api/v1/ai/chat?user_id=1", json=message_data)
        
        # 获取聊天历史
        response = client.get("/api/v1/ai/chat/history?user_id=1")
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "total" in data
        assert len(data["messages"]) > 0
    
    def test_get_recent_chat_history(self, client):
        """测试获取最近聊天历史"""
        response = client.get("/api/v1/ai/chat/history/recent?user_id=1&days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "total" in data
    
    def test_get_chat_sessions(self, client):
        """测试获取聊天会话列表"""
        response = client.get("/api/v1/ai/chat/sessions?user_id=1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_chat_health_check(self, client):
        """测试健康检查"""
        response = client.get("/api/v1/ai/chat/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["service"] == "ai_chat"
        assert data["data"]["status"] == "healthy"
    
    def test_invalid_user_id(self, client):
        """测试无效用户ID"""
        message_data = {
            "content": "测试消息",
            "session_id": None
        }
        
        response = client.post(
            "/api/v1/ai/chat",  # 缺少user_id参数
            json=message_data
        )
        
        assert response.status_code == 422  # 验证错误
    
    def test_empty_message(self, client):
        """测试空消息"""
        message_data = {
            "content": "",  # 空内容
            "session_id": None
        }
        
        response = client.post(
            "/api/v1/ai/chat?user_id=1",
            json=message_data
        )
        
        assert response.status_code == 422  # 验证错误

if __name__ == "__main__":
    pytest.main([__file__]) 