from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

# 模拟对话数据
mock_conversations = []
mock_messages = []

@router.post("/chat")
async def send_message(message_data: dict):
    """发送AI对话消息"""
    user_message = message_data.get("message", "")
    conversation_id = message_data.get("conversationId")
    
    # 模拟AI回复
    ai_responses = [
        "很好的问题！根据你的学习情况，我建议你可以尝试番茄工作法来提高效率。",
        "从你的学习数据来看，你在数学方面投入了很多时间，建议适当调整学习计划，增加其他科目的时间。",
        "你的学习习惯很好，继续保持！建议你可以尝试制定更具体的学习目标。",
        "根据学习心理学，分散学习比集中学习效果更好，建议你将长时间学习分解为多个短时间段。"
    ]
    
    import random
    ai_reply = random.choice(ai_responses)
    
    # 创建新对话（如果不存在）
    if not conversation_id:
        conversation_id = len(mock_conversations) + 1
        mock_conversations.append({
            "id": conversation_id,
            "title": user_message[:20] + "...",
            "created_at": datetime.now().isoformat()
        })
    
    # 添加用户消息
    user_msg = {
        "id": len(mock_messages) + 1,
        "conversation_id": conversation_id,
        "type": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    }
    mock_messages.append(user_msg)
    
    # 添加AI回复
    ai_msg = {
        "id": len(mock_messages) + 1,
        "conversation_id": conversation_id,
        "type": "ai",
        "content": ai_reply,
        "timestamp": datetime.now().isoformat()
    }
    mock_messages.append(ai_msg)
    
    return {
        "conversation_id": conversation_id,
        "user_message": user_msg,
        "ai_response": ai_msg
    }

@router.get("/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: int):
    """获取对话历史"""
    messages = [msg for msg in mock_messages if msg["conversation_id"] == conversation_id]
    return {"messages": messages}

@router.get("/conversations/user/{user_id}")
async def get_user_conversations(user_id: int):
    """获取用户的所有对话列表"""
    return {"conversations": mock_conversations}

@router.get("/analysis/{user_id}")
async def get_study_analysis(user_id: int, range: str = "week"):
    """获取AI学习分析"""
    return {
        "analysis": {
            "overall_performance": "良好",
            "strengths": ["时间管理", "学习专注度"],
            "improvements": ["学科平衡", "休息安排"],
            "suggestions": [
                "建议增加英语学习时间",
                "适当安排休息时间",
                "可以尝试不同的学习方法"
            ],
            "attention_score": 85,
            "efficiency_score": 78
        },
        "range": range
    }

@router.post("/suggestions")
async def get_study_suggestions(request_data: dict):
    """获取AI学习建议"""
    user_id = request_data.get("userId")
    current_task = request_data.get("currentTask", "")
    
    suggestions = [
        {
            "type": "method",
            "title": "番茄工作法",
            "description": "25分钟专注学习，5分钟休息，提高效率"
        },
        {
            "type": "schedule",
            "title": "学习时间调整",
            "description": "建议在上午9-11点进行高难度学习"
        },
        {
            "type": "break",
            "title": "适当休息",
            "description": "连续学习2小时后，建议休息15-20分钟"
        }
    ]
    
    return {"suggestions": suggestions} 