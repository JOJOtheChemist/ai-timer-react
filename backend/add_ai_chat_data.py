#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为user 101添加AI聊天测试数据
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

def add_ai_chat_data(db):
    """添加AI聊天数据"""
    print("\n" + "="*50)
    print("开始添加AI聊天数据...")
    print("="*50)
    
    user_id = 101
    now = datetime.now()
    
    # 聊天对话数据
    conversations = [
        {
            "question": "我英语基础很差，六级才420分，考研英语一有希望吗？",
            "answer": """你好！六级420分说明你有一定的英语基础，考研英语一是完全有希望的！很多同学从更低的基础开始，最终也取得了不错的成绩。

我给你几点建议：

1. **单词是基础**
   - 每天坚持背200个单词
   - 使用艾宾浩斯遗忘曲线复习法
   - 重点记忆考研高频词汇

2. **阅读是关键**
   - 从精读开始，每天一篇真题阅读
   - 逐句分析长难句
   - 总结错题原因

3. **作文要积累**
   - 整理自己的作文模板
   - 每周练习3篇作文
   - 背诵优秀范文

4. **制定学习计划**
   - 基础阶段（3-4个月）：单词+语法
   - 强化阶段（3-4个月）：真题+技巧
   - 冲刺阶段（2个月）：模拟+查漏补缺

坚持8个月，从52分到82分是完全可能的！加油！💪""",
            "tags": ["英语学习", "考研规划", "学习建议"],
            "create_time": now - timedelta(days=5, hours=10)
        },
        {
            "question": "如何制定每天的学习时间表？",
            "answer": """制定每天的学习时间表需要考虑以下几个要点：

1. **了解自己的高效时段**
   - 早晨：适合背单词、记忆知识点
   - 上午：适合学习难度较大的科目（如数学）
   - 下午：适合做题、巩固练习
   - 晚上：适合总结复习、查漏补缺

2. **合理分配时间**
   - 专业课：每天3-4小时
   - 数学：每天2-3小时
   - 英语：每天2小时
   - 政治：每天1-1.5小时

3. **使用番茄工作法**
   - 25分钟专注学习
   - 5分钟休息
   - 4个番茄钟后休息15-30分钟

4. **灵活调整**
   - 根据自己的进度调整
   - 保证每周至少休息半天
   - 适当的运动和娱乐

你可以在我们的"首页时间表"功能中创建你的个性化时间表！📅""",
            "tags": ["时间管理", "学习规划", "效率提升"],
            "create_time": now - timedelta(days=3, hours=14)
        },
        {
            "question": "番茄工作法真的有用吗？",
            "answer": """番茄工作法确实是一个非常有效的时间管理方法！它的核心优势在于：

✅ **优点：**
1. **提高专注力**：25分钟内拒绝一切干扰
2. **减少疲劳**：定时休息，保持大脑活力
3. **可量化进度**：每个番茄钟都是一次小成就
4. **培养习惯**：长期使用能提高时间感知能力

📊 **使用技巧：**
- 设置明确的任务目标
- 准备一个计时器
- 休息时间远离手机
- 记录每天完成的番茄钟数量

⚠️ **注意事项：**
- 刚开始可能不太适应，需要1-2周适应期
- 有些任务可能需要调整时长（如数学大题）
- 不是所有学习场景都适合（如考试时）

建议你先试用一周，看看是否适合自己！很多学长学姐都反馈效果很好。""",
            "tags": ["学习方法", "番茄工作法", "时间管理"],
            "create_time": now - timedelta(days=2, hours=9)
        },
        {
            "question": "考研需要报班吗？",
            "answer": """是否报班需要根据你的个人情况来决定：

🎯 **建议报班的情况：**
1. 基础较弱，需要系统学习
2. 自制力较差，需要监督
3. 专业课资料难找
4. 需要答疑和指导

💪 **可以自学的情况：**
1. 基础较好，学习能力强
2. 自制力强，有明确规划
3. 能找到靠谱的学习资料
4. 有学长学姐指导

💡 **折中方案：**
- 公共课：购买网课（性价比高）
- 专业课：找目标院校的学长学姐一对一辅导
- 使用我们平台的导师服务，针对性指导

记住：**报班不是成功的必要条件**，关键是找到适合自己的学习方法，并坚持执行！

你可以在"导师推荐"页面找到适合你的辅导老师！👨‍🏫""",
            "tags": ["考研准备", "报班建议", "学习规划"],
            "create_time": now - timedelta(days=1, hours=16)
        },
        {
            "question": "如何保持学习动力？",
            "answer": """保持学习动力确实是考研路上的一大挑战！这里有几个有效的方法：

🎯 **设定清晰目标：**
- 长期目标：目标院校和专业
- 中期目标：每月学习计划
- 短期目标：每周、每日任务
- 记录进度，看到自己的成长

🏆 **建立奖励机制：**
- 完成每日目标，奖励自己喜欢的事
- 完成阶段性目标，给自己小礼物
- 定期总结成就感

👥 **找到研友：**
- 互相监督，互相鼓励
- 分享学习资源和经验
- 但避免攀比和负面情绪

💪 **调整心态：**
- 接受学习的枯燥期
- 相信努力一定有回报
- 适当放松，避免过度焦虑

📊 **使用工具：**
- 在我们平台打卡记录学习时长
- 查看排行榜，激励自己
- 参考成功案例，增强信心

记住：**考研是一场马拉松，不是短跑**。保持稳定的节奏比一时的冲刺更重要！加油！💪""",
            "tags": ["心态调整", "学习动力", "考研心得"],
            "create_time": now - timedelta(hours=5)
        }
    ]
    
    for i, conv in enumerate(conversations):
        try:
            session_id = f"session_{user_id}_{i+1}"
            
            # 插入用户问题
            query_user = text("""
                INSERT INTO ai_chat_record 
                (user_id, session_id, role, content, create_time)
                VALUES 
                (:user_id, :session_id, 'user', :content, :create_time)
            """)
            
            db.execute(query_user, {
                "user_id": user_id,
                "session_id": session_id,
                "content": conv["question"],
                "create_time": conv["create_time"]
            })
            
            # 插入AI回答
            query_ai = text("""
                INSERT INTO ai_chat_record 
                (user_id, session_id, role, content, analysis_tags, create_time)
                VALUES 
                (:user_id, :session_id, 'ai', :content, CAST(:tags AS jsonb), :create_time)
            """)
            
            db.execute(query_ai, {
                "user_id": user_id,
                "session_id": session_id,
                "content": conv["answer"],
                "tags": json.dumps(conv["tags"]),
                "create_time": conv["create_time"] + timedelta(seconds=5)
            })
            
            db.commit()
            print(f"✅ 成功添加AI对话: {conv['question'][:30]}...")
        except Exception as e:
            db.rollback()
            print(f"❌ 添加AI对话失败: {e}")

def main():
    """主函数"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("开始为user 101添加AI聊天测试数据")
        print("="*60)
        
        add_ai_chat_data(db)
        
        print("\n" + "="*60)
        print("✅ AI聊天数据添加完成！")
        print("="*60)
        print("\n数据概览：")
        print("- AI对话记录：5条")
        print("- 涵盖主题：英语学习、时间管理、学习方法、报班建议、心态调整")
        print("\n所有数据已绑定到user 101")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main() 