#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为所有页面添加真实测试数据
包括：学习方法、导师推荐、成功案例
"""

import sys
import os
from datetime import datetime, timedelta
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings

# 创建数据库连接
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_study_methods(db):
    """添加学习方法数据"""
    print("\n" + "="*50)
    print("开始添加学习方法数据...")
    print("="*50)
    
    methods_data = [
        {
            "name": "艾宾浩斯复习四步法",
            "category": "common",
            "type": "全学科",
            "description": "基于艾宾浩斯遗忘曲线的科学复习方法，通过多次重复记忆来巩固知识点。",
            "steps": json.dumps([
                "第一步：初次学习后5-10分钟进行第一次复习",
                "第二步：24小时后进行第二次复习",
                "第三步：一周后进行第三次复习",
                "第四步：一个月后进行第四次复习",
                "注意：每次复习要主动回忆，不要只是被动看书"
            ]),
            "scene": "适合需要大量记忆的学科，如英语单词、专业课知识点等",
            "checkin_count": 2856,
            "rating": 4.8,
            "review_count": 456
        },
        {
            "name": "番茄工作法",
            "category": "common",
            "type": "时间管理",
            "description": "将工作时间分割成25分钟的专注时段，配合短暂休息，提高学习效率。",
            "steps": json.dumps([
                "第一步：设定25分钟倒计时，全神贯注学习",
                "第二步：完成后休息5分钟，放松大脑",
                "第三步：完成4个番茄钟后，休息15-30分钟",
                "第四步：记录每个番茄钟的学习内容和效果",
                "技巧：番茄钟期间拒绝一切干扰"
            ]),
            "scene": "适合容易分心、需要提高专注力的学习场景",
            "checkin_count": 3421,
            "rating": 4.7,
            "review_count": 678
        },
        {
            "name": "费曼学习法",
            "category": "common",
            "type": "理解深化",
            "description": "通过向他人解释来检验自己的理解程度，发现知识盲点。",
            "steps": json.dumps([
                "第一步：选择一个要学习的概念",
                "第二步：假设你要教给一个完全不懂的人",
                "第三步：用简单的语言写下或说出你的解释",
                "第四步：发现卡壳的地方，回去重新学习",
                "第五步：简化语言，用类比来帮助理解"
            ]),
            "scene": "适合理解复杂概念，如数学定理、物理原理等",
            "checkin_count": 1987,
            "rating": 4.9,
            "review_count": 321
        },
        {
            "name": "康奈尔笔记法",
            "category": "common",
            "type": "笔记整理",
            "description": "系统化的笔记方法，将笔记分为线索栏、笔记栏和总结栏三部分。",
            "steps": json.dumps([
                "第一步：准备笔记本，划分为三个区域",
                "第二步：右侧笔记栏记录课堂内容",
                "第三步：左侧线索栏写下关键词和问题",
                "第四步：底部总结栏概括本页要点",
                "第五步：复习时先看线索栏，尝试回忆内容"
            ]),
            "scene": "适合课堂笔记、阅读笔记等需要系统整理的场景",
            "checkin_count": 1543,
            "rating": 4.6,
            "review_count": 234
        },
        {
            "name": "间隔重复记忆法",
            "category": "common",
            "type": "记忆强化",
            "description": "通过逐渐增加复习间隔来提高长期记忆效果。",
            "steps": json.dumps([
                "第一步：第一次学习后立即复习",
                "第二步：间隔1天进行第二次复习",
                "第三步：间隔3天进行第三次复习",
                "第四步：间隔7天进行第四次复习",
                "第五步：间隔15天进行第五次复习"
            ]),
            "scene": "适合英语单词、专业术语等需要长期记忆的内容",
            "checkin_count": 2134,
            "rating": 4.7,
            "review_count": 398
        }
    ]
    
    now = datetime.now()
    for i, method in enumerate(methods_data):
        try:
            query = text("""
                INSERT INTO study_method 
                (name, category, type, description, steps, scene, checkin_count, rating, review_count, status, create_time, update_time)
                VALUES 
                (:name, :category, :type, :description, CAST(:steps AS jsonb), :scene, :checkin_count, :rating, :review_count, 0, :create_time, :update_time)
                ON CONFLICT DO NOTHING
            """)
            
            db.execute(query, {
                "name": method["name"],
                "category": method["category"],
                "type": method["type"],
                "description": method["description"],
                "steps": method["steps"],
                "scene": method["scene"],
                "checkin_count": method["checkin_count"],
                "rating": method["rating"],
                "review_count": method["review_count"],
                "create_time": now - timedelta(days=30-i),
                "update_time": now - timedelta(days=30-i)
            })
            db.commit()
            print(f"✅ 成功添加学习方法: {method['name']}")
        except Exception as e:
            db.rollback()
            print(f"❌ 添加学习方法失败 {method['name']}: {e}")

def add_tutors(db):
    """添加导师数据"""
    print("\n" + "="*50)
    print("开始添加导师数据...")
    print("="*50)
    
    # 首先创建导师用户
    tutors_data = [
        {
            "id": 201,
            "username": "王英语老师",
            "avatar": "/avatars/avatar1.png",
            "type": 1,  # 认证导师
            "domain": "考研英语",
            "education": "北京外国语大学 英语语言文学硕士",
            "experience": "2020年考研英语一87分，阅读满分",
            "work_experience": "5年考研英语辅导经验，累计指导学员300+",
            "philosophy": "英语学习没有捷径，但有方法。重在积累，贵在坚持。",
            "rating": 98,
            "student_count": 156,
            "success_rate": 89,
            "monthly_guide_count": 23
        },
        {
            "id": 202,
            "username": "李数学导师",
            "avatar": "/avatars/avatar2.png",
            "type": 1,  # 认证导师
            "domain": "考研数学",
            "education": "清华大学 数学系博士",
            "experience": "2019年考研数学一150分满分",
            "work_experience": "6年考研数学辅导经验，专注高等数学、线性代数",
            "philosophy": "数学学习重在理解本质，通过大量练习巩固知识点。",
            "rating": 96,
            "student_count": 198,
            "success_rate": 92,
            "monthly_guide_count": 31
        },
        {
            "id": 203,
            "username": "张政治学长",
            "avatar": "/avatars/avatar3.png",
            "type": 0,  # 普通导师
            "domain": "考研政治",
            "education": "人民大学 马克思主义理论硕士",
            "experience": "2021年考研政治82分，选择题仅错2题",
            "work_experience": "3年考研政治辅导经验，擅长选择题技巧",
            "philosophy": "政治学习要抓住重点，理解框架，掌握答题技巧。",
            "rating": 94,
            "student_count": 87,
            "success_rate": 85,
            "monthly_guide_count": 15
        },
        {
            "id": 204,
            "username": "陈专业课导师",
            "avatar": "/avatars/avatar4.jpg",
            "type": 1,  # 认证导师
            "domain": "计算机专业课",
            "education": "浙江大学 计算机科学与技术博士",
            "experience": "2018年考研专业课145分，数据结构满分",
            "work_experience": "7年计算机考研辅导，熟悉408统考和自命题",
            "philosophy": "专业课学习要系统化，注重代码实践和算法理解。",
            "rating": 97,
            "student_count": 234,
            "success_rate": 91,
            "monthly_guide_count": 28
        }
    ]
    
    now = datetime.now()
    for tutor in tutors_data:
        try:
            # 创建导师账号
            user_query = text("""
                INSERT INTO "user" 
                (id, username, phone, password_hash, avatar, goal, major, created_at, updated_at)
                VALUES 
                (:id, :username, :phone, :password_hash, :avatar, :goal, :major, :created_at, :updated_at)
                ON CONFLICT (id) DO UPDATE SET
                    username = EXCLUDED.username,
                    avatar = EXCLUDED.avatar,
                    goal = EXCLUDED.goal,
                    major = EXCLUDED.major
            """)
            
            db.execute(user_query, {
                "id": tutor["id"],
                "username": tutor["username"],
                "phone": f"138000002{tutor['id']-200:02d}",
                "password_hash": f"hashed_password_{tutor['id']}",
                "avatar": tutor["avatar"],
                "goal": f"{tutor['domain']}辅导",
                "major": tutor["domain"],
                "created_at": now - timedelta(days=365),
                "updated_at": now
            })
            db.commit()
            print(f"✅ 成功创建导师账号: {tutor['username']}")
            
            # 创建导师信息
            tutor_query = text("""
                INSERT INTO tutor 
                (id, username, avatar, type, domain, education, experience, work_experience, philosophy, 
                rating, student_count, success_rate, monthly_guide_count, status, create_time, update_time)
                VALUES 
                (:id, :username, :avatar, :type, :domain, :education, :experience, :work_experience, :philosophy,
                :rating, :student_count, :success_rate, :monthly_guide_count, 0, :create_time, :update_time)
                ON CONFLICT (id) DO UPDATE SET
                    username = EXCLUDED.username,
                    avatar = EXCLUDED.avatar,
                    type = EXCLUDED.type,
                    domain = EXCLUDED.domain,
                    rating = EXCLUDED.rating,
                    student_count = EXCLUDED.student_count
            """)
            
            db.execute(tutor_query, {
                "id": tutor["id"],
                "username": tutor["username"],
                "avatar": tutor["avatar"],
                "type": tutor["type"],
                "domain": tutor["domain"],
                "education": tutor["education"],
                "experience": tutor["experience"],
                "work_experience": tutor["work_experience"],
                "philosophy": tutor["philosophy"],
                "rating": tutor["rating"],
                "student_count": tutor["student_count"],
                "success_rate": tutor["success_rate"],
                "monthly_guide_count": tutor["monthly_guide_count"],
                "create_time": now - timedelta(days=365),
                "update_time": now
            })
            db.commit()
            print(f"✅ 成功添加导师信息: {tutor['username']}")
            
            # 为每个导师添加服务项目
            services = [
                {
                    "name": "一对一答疑咨询",
                    "price": 30,
                    "description": "针对学习过程中的具体问题进行解答",
                    "service_type": "consultation",
                    "estimated_hours": 0.5
                },
                {
                    "name": "学习规划定制",
                    "price": 88,
                    "description": "根据个人情况定制专属学习计划",
                    "service_type": "planning",
                    "estimated_hours": 2.0
                },
                {
                    "name": "作业批改点评",
                    "price": 50,
                    "description": "详细批改作业并提供改进建议",
                    "service_type": "correction",
                    "estimated_hours": 1.0
                }
            ]
            
            for service in services:
                service_query = text("""
                    INSERT INTO tutor_service 
                    (tutor_id, name, price, description, service_type, estimated_hours, is_active, create_time, update_time)
                    VALUES 
                    (:tutor_id, :name, :price, :description, :service_type, :estimated_hours, 1, :create_time, :update_time)
                """)
                
                db.execute(service_query, {
                    "tutor_id": tutor["id"],
                    "name": service["name"],
                    "price": service["price"],
                    "description": service["description"],
                    "service_type": service["service_type"],
                    "estimated_hours": service["estimated_hours"],
                    "create_time": now - timedelta(days=300),
                    "update_time": now
                })
                db.commit()
                
            print(f"✅ 成功添加导师服务项目: {len(services)}个")
            
        except Exception as e:
            db.rollback()
            print(f"❌ 添加导师失败 {tutor['username']}: {e}")

def add_success_cases(db):
    """添加成功案例数据"""
    print("\n" + "="*50)
    print("开始添加成功案例数据...")
    print("="*50)
    
    cases_data = [
        {
            "user_id": 101,
            "title": "二战上岸985：从六级420到考研英语82分的逆袭之路",
            "icon": "📚",
            "duration": "8个月",
            "tags": json.dumps(["考研", "英语逆袭", "二战", "日均4h"]),
            "author_name": "@李同学",
            "view_count": 12453,
            "like_count": 2341,
            "collect_count": 1876,
            "is_hot": 1,
            "preview_days": 3,
            "price": "50钻石查看",
            "content": """# 我的考研英语逆袭经历

## 基础情况
- 一战英语52分，六级420分
- 二战目标：985高校
- 备考时长：8个月
- 最终成绩：英语一82分

## 学习方法
### 单词篇
每天坚持背200个单词，使用艾宾浩斯遗忘曲线复习法...

### 阅读篇  
从精读开始，每天一篇真题阅读，逐句分析...

### 作文篇
整理自己的作文模板，每周练习3篇...""",
            "summary": "二战考生通过系统学习，英语从52分提升至82分的完整经验分享",
            "difficulty_level": 4,
            "category": "考研",
            "status": 1
        },
        {
            "user_id": 102,
            "title": "数学从0基础到140+：我的高数学习之路",
            "icon": "📐",
            "duration": "10个月",
            "tags": json.dumps(["考研数学", "零基础", "高分经验", "日均6h"]),
            "author_name": "@王同学",
            "view_count": 9876,
            "like_count": 1987,
            "collect_count": 1543,
            "is_hot": 1,
            "preview_days": 3,
            "price": "88钻石查看",
            "content": """# 数学零基础到140+的学习历程

## 我的背景
本科文科生，数学基础几乎为零...

## 学习计划
### 基础阶段（3个月）
系统学习高数、线代、概率论的基础知识...""",
            "summary": "文科生跨考理工科，数学从零基础到140+的完整学习路径",
            "difficulty_level": 5,
            "category": "考研",
            "status": 1
        },
        {
            "user_id": 103,
            "title": "在职考研：如何平衡工作与学习",
            "icon": "💼",
            "duration": "12个月",
            "tags": json.dumps(["在职考研", "时间管理", "工作学习平衡"]),
            "author_name": "@陈同学",
            "view_count": 7654,
            "like_count": 1543,
            "collect_count": 1234,
            "is_hot": 1,
            "preview_days": 3,
            "price": "68钻石查看",
            "content": """# 在职考研的时间管理秘诀

## 背景介绍
工作三年后决定考研，每天只有3-4小时学习时间...

## 时间规划
早上6:00-7:30：英语学习
晚上8:00-11:00：专业课复习...""",
            "summary": "在职人员如何利用有限时间高效备考，最终成功上岸",
            "difficulty_level": 4,
            "category": "考研",
            "status": 1
        },
        {
            "user_id": 104,
            "title": "三个月突破专业课：408统考145分经验",
            "icon": "💻",
            "duration": "3个月",
            "tags": json.dumps(["计算机", "408统考", "短期突破", "高分技巧"]),
            "author_name": "@赵同学",
            "view_count": 11234,
            "like_count": 2198,
            "collect_count": 1987,
            "is_hot": 1,
            "preview_days": 3,
            "price": "78钻石查看",
            "content": """# 408统考高分秘籍

## 考试成绩
数据结构：满分
计算机组成原理：48/50
操作系统：47/50
计算机网络：50/50...""",
            "summary": "计算机专业课408统考3个月冲刺，最终145分的学习方法",
            "difficulty_level": 5,
            "category": "考研",
            "status": 1
        },
        {
            "user_id": 105,
            "title": "政治80+：选择题满分的刷题技巧",
            "icon": "🎯",
            "duration": "4个月",
            "tags": json.dumps(["考研政治", "选择题技巧", "高分经验"]),
            "author_name": "@孙同学",
            "view_count": 8765,
            "like_count": 1678,
            "collect_count": 1345,
            "is_hot": 0,
            "preview_days": 3,
            "price": "45钻石查看",
            "content": """# 政治选择题满分攻略

## 我的成绩
选择题：50分（满分）
大题：33分
总分：83分...""",
            "summary": "考研政治选择题满分，总分80+的刷题方法和答题技巧",
            "difficulty_level": 3,
            "category": "考研",
            "status": 1
        }
    ]
    
    # 创建额外的用户（案例作者）
    for user_id in [102, 103, 104, 105]:
        try:
            user_query = text("""
                INSERT INTO "user" 
                (id, username, phone, password_hash, avatar, goal, major, created_at, updated_at)
                VALUES 
                (:id, :username, :phone, :password_hash, :avatar, :goal, :major, :created_at, :updated_at)
                ON CONFLICT (id) DO NOTHING
            """)
            
            db.execute(user_query, {
                "id": user_id,
                "username": f"用户{user_id}",
                "phone": f"138000001{user_id:02d}",
                "password_hash": f"hashed_password_{user_id}",
                "avatar": f"/avatars/avatar{((user_id-1) % 5) + 1}.png",
                "goal": "考研上岸",
                "major": "各专业",
                "created_at": datetime.now() - timedelta(days=400),
                "updated_at": datetime.now()
            })
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"创建用户{user_id}时出错: {e}")
    
    now = datetime.now()
    for i, case in enumerate(cases_data):
        try:
            query = text("""
                INSERT INTO success_case 
                (user_id, title, icon, duration, tags, author_name, view_count, like_count, collect_count, 
                is_hot, preview_days, price, content, summary, difficulty_level, category, status, 
                create_time, update_time, publish_time)
                VALUES 
                (:user_id, :title, :icon, :duration, CAST(:tags AS jsonb), :author_name, :view_count, 
                :like_count, :collect_count, :is_hot, :preview_days, :price, :content, :summary, 
                :difficulty_level, :category, :status, :create_time, :update_time, :publish_time)
            """)
            
            publish_time = now - timedelta(days=60-i*10)
            db.execute(query, {
                "user_id": case["user_id"],
                "title": case["title"],
                "icon": case["icon"],
                "duration": case["duration"],
                "tags": case["tags"],
                "author_name": case["author_name"],
                "view_count": case["view_count"],
                "like_count": case["like_count"],
                "collect_count": case["collect_count"],
                "is_hot": case["is_hot"],
                "preview_days": case["preview_days"],
                "price": case["price"],
                "content": case["content"],
                "summary": case["summary"],
                "difficulty_level": case["difficulty_level"],
                "category": case["category"],
                "status": case["status"],
                "create_time": publish_time,
                "update_time": now,
                "publish_time": publish_time
            })
            db.commit()
            print(f"✅ 成功添加成功案例: {case['title']}")
        except Exception as e:
            db.rollback()
            print(f"❌ 添加成功案例失败 {case['title']}: {e}")

def main():
    """主函数"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("开始为所有页面添加真实测试数据")
        print("目标用户：user 101")
        print("="*60)
        
        # 添加学习方法数据
        add_study_methods(db)
        
        # 添加导师数据
        add_tutors(db)
        
        # 添加成功案例数据
        add_success_cases(db)
        
        print("\n" + "="*60)
        print("✅ 所有数据添加完成！")
        print("="*60)
        print("\n数据概览：")
        print("- 学习方法：5个")
        print("- 导师信息：4个（每个导师3项服务）")
        print("- 成功案例：5个")
        print("\n所有数据已与user 101及相关用户绑定")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main() 