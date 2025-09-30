from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter()

# 模拟导师数据
mock_tutors = [
    {
        "id": 1,
        "name": "张教授",
        "avatar": "👨‍🏫",
        "specialties": ["数学", "物理"],
        "rating": 4.8,
        "students_count": 156,
        "experience": "10年教学经验",
        "description": "专业数学导师，擅长高等数学和线性代数教学",
        "price_per_hour": 200,
        "availability": ["周一", "周三", "周五"]
    },
    {
        "id": 2,
        "name": "李老师",
        "avatar": "👩‍🏫",
        "specialties": ["英语", "文学"],
        "rating": 4.9,
        "students_count": 203,
        "experience": "8年教学经验",
        "description": "英语专业导师，雅思托福专家",
        "price_per_hour": 180,
        "availability": ["周二", "周四", "周六"]
    }
]

# 模拟评论数据
mock_comments = [
    {
        "id": 1,
        "tutor_id": 1,
        "user_name": "学生A",
        "rating": 5,
        "comment": "张教授讲解很清楚，数学思维很强！",
        "created_at": "2023-11-15T10:00:00"
    },
    {
        "id": 2,
        "tutor_id": 1,
        "user_name": "学生B",
        "rating": 4,
        "comment": "很有耐心，会根据学生情况调整教学方法",
        "created_at": "2023-11-10T14:30:00"
    }
]

@router.get("/")
async def get_tutors(specialty: str = None, rating_min: float = 0):
    """获取导师列表"""
    tutors = mock_tutors
    
    if specialty:
        tutors = [t for t in tutors if specialty in t["specialties"]]
    
    if rating_min > 0:
        tutors = [t for t in tutors if t["rating"] >= rating_min]
    
    return {"tutors": tutors, "total": len(tutors)}

@router.get("/{tutor_id}")
async def get_tutor_profile(tutor_id: int):
    """获取导师详细信息"""
    tutor = next((t for t in mock_tutors if t["id"] == tutor_id), None)
    if not tutor:
        raise HTTPException(status_code=404, detail="导师不存在")
    
    return {"tutor": tutor}

@router.get("/{tutor_id}/comments")
async def get_tutor_comments(tutor_id: int, page: int = 1, limit: int = 10):
    """获取导师评论列表"""
    tutor_comments = [c for c in mock_comments if c["tutor_id"] == tutor_id]
    
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "comments": tutor_comments[start:end],
        "total": len(tutor_comments),
        "page": page,
        "limit": limit
    }

@router.post("/{tutor_id}/comments")
async def add_tutor_comment(tutor_id: int, comment_data: dict):
    """添加导师评论"""
    new_comment = {
        "id": len(mock_comments) + 1,
        "tutor_id": tutor_id,
        "user_name": comment_data.get("user_name", "匿名用户"),
        "rating": comment_data.get("rating", 5),
        "comment": comment_data.get("comment", ""),
        "created_at": datetime.now().isoformat()
    }
    
    mock_comments.append(new_comment)
    return {"message": "评论添加成功", "comment": new_comment}

@router.post("/{tutor_id}/apply")
async def apply_to_tutor(tutor_id: int, application_data: dict):
    """申请成为某导师的学生"""
    tutor = next((t for t in mock_tutors if t["id"] == tutor_id), None)
    if not tutor:
        raise HTTPException(status_code=404, detail="导师不存在")
    
    application = {
        "id": 1,
        "tutor_id": tutor_id,
        "student_name": application_data.get("student_name", ""),
        "message": application_data.get("message", ""),
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    return {"message": "申请提交成功", "application": application}

@router.post("/{tutor_id}/book")
async def book_tutor_session(tutor_id: int, session_data: dict):
    """预约导师指导时间"""
    tutor = next((t for t in mock_tutors if t["id"] == tutor_id), None)
    if not tutor:
        raise HTTPException(status_code=404, detail="导师不存在")
    
    booking = {
        "id": 1,
        "tutor_id": tutor_id,
        "student_id": session_data.get("student_id"),
        "date": session_data.get("date"),
        "time": session_data.get("time"),
        "duration": session_data.get("duration", 60),
        "subject": session_data.get("subject", ""),
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    
    return {"message": "预约成功", "booking": booking} 