#!/usr/bin/env python3
"""
添加成功案例测试数据
"""
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import SessionLocal
from models.case import SuccessCase

def add_success_cases():
    """添加成功案例测试数据"""
    db = SessionLocal()
    
    try:
        print("🚀 开始添加成功案例数据...\n")
        
        # 清空现有案例
        print("🗑️  清空现有案例...")
        db.query(SuccessCase).delete()
        db.commit()
        print("✅ 已清空\n")
        
        # 创建案例数据
        print("1️⃣ 创建成功案例...")
        
        cases_data = [
            {
                "title": "976小时高考逆袭200分上一本",
                "category": "高考",
                "duration": "976h",
                "icon": "📚",
                "tags": ["高考", "失恋逆袭", "日均13h"],
                "author_name": "小夏",
                "view_count": 1286,
                "is_hot": 1,
                "preview_days": 3,
                "price": "88",
                "content": "从失恋低谷到逆袭上一本的完整学习计划。通过科学的时间管理和高效学习方法，实现了200分的巨大突破。详细记录了每天的学习计划、心态调整和方法总结。",
                "summary": "失恋逆袭，976小时从低谷到一本",
                "status": 1  # 已发布
            },
            {
                "title": "4440小时会计学上岸CPA全科",
                "category": "考证",
                "duration": "4440h",
                "icon": "💼",
                "tags": ["考证", "在职备考", "3年规划"],
                "author_name": "李会计",
                "view_count": 952,
                "is_hot": 0,
                "preview_days": 3,
                "price": "98",
                "content": "在职3年通过CPA全科的完整经验。合理规划工作与学习时间，高效通过六门考试。",
                "summary": "在职备考，3年通过CPA全科",
                "status": 1
            },
            {
                "title": "1800小时0基础逆袭Python开发",
                "category": "技能学习",
                "duration": "1800h",
                "icon": "💻",
                "tags": ["技能", "0基础", "转行"],
                "author_name": "张码农",
                "view_count": 734,
                "is_hot": 0,
                "preview_days": 3,
                "price": "78",
                "content": "从完全零基础到成功转行Python开发。系统的学习路线和项目实战经验分享。",
                "summary": "0基础转行Python开发",
                "status": 1
            },
            {
                "title": "2100小时考研英语从40分到82分",
                "category": "考研",
                "duration": "2100h",
                "icon": "📚",
                "tags": ["考研", "0基础"],
                "author_name": "王老师",
                "view_count": 621,
                "is_hot": 1,
                "preview_days": 3,
                "price": "88",
                "content": "英语零基础到考研82分的完整学习路径。包含单词、语法、阅读、写作的系统方法。",
                "summary": "考研英语从40到82分",
                "status": 1
            },
            {
                "title": "1500小时0基础学UI设计入职大厂",
                "category": "技能学习",
                "duration": "1500h",
                "icon": "🎨",
                "tags": ["技能学习", "转行", "日均6h"],
                "author_name": "小美学姐",
                "view_count": 589,
                "is_hot": 0,
                "preview_days": 3,
                "price": "68",
                "content": "UI设计从入门到入职大厂的完整路线。包含设计理论、工具使用、作品集制作。",
                "summary": "0基础UI设计入职大厂",
                "status": 1
            },
            {
                "title": "2800小时在职备考银行秋招上岸",
                "category": "职场晋升",
                "duration": "2800h",
                "icon": "🏦",
                "tags": ["职场晋升", "在职备考"],
                "author_name": "陈经理",
                "view_count": 512,
                "is_hot": 0,
                "preview_days": 3,
                "price": "98",
                "content": "在职备考银行秋招的完整经验。包含笔试、面试、时间管理的全方位指导。",
                "summary": "在职备考银行秋招",
                "status": 1
            },
            {
                "title": "3200小时考研数学从60到140分",
                "category": "考研",
                "duration": "3200h",
                "icon": "📊",
                "tags": ["考研", "进阶提升", "日均8h"],
                "author_name": "刘数学",
                "view_count": 892,
                "is_hot": 1,
                "preview_days": 3,
                "price": "98",
                "content": "考研数学从及格线到高分的突破之路。系统的知识框架和刷题策略。",
                "summary": "考研数学从60到140分",
                "status": 1
            },
            {
                "title": "2400小时二战上岸985计算机",
                "category": "考研",
                "duration": "2400h",
                "icon": "💻",
                "tags": ["考研", "二战", "985"],
                "author_name": "赵同学",
                "view_count": 1023,
                "is_hot": 1,
                "preview_days": 3,
                "price": "118",
                "content": "二战上岸985计算机的完整复习经验。失败经验总结和成功策略分享。",
                "summary": "二战上岸985计算机",
                "status": 1
            },
            {
                "title": "1200小时宝妈备考教师资格证",
                "category": "考证",
                "duration": "1200h",
                "icon": "👩‍🏫",
                "tags": ["考证", "宝妈备考", "碎片时间"],
                "author_name": "孙妈妈",
                "view_count": 456,
                "is_hot": 0,
                "preview_days": 3,
                "price": "58",
                "content": "宝妈利用碎片时间备考教师资格证的经验。时间管理和高效学习方法。",
                "summary": "宝妈碎片时间备考",
                "status": 1
            },
            {
                "title": "3600小时法考从零到过",
                "category": "考证",
                "duration": "3600h",
                "icon": "⚖️",
                "tags": ["考证", "0基础", "非法学"],
                "author_name": "周律师",
                "view_count": 678,
                "is_hot": 0,
                "preview_days": 3,
                "price": "128",
                "content": "非法学背景通过法考的完整经验。知识体系搭建和记忆方法分享。",
                "summary": "非法学通过法考",
                "status": 1
            },
            {
                "title": "800小时雅思从5.5到7.5",
                "category": "考证",
                "duration": "800h",
                "icon": "🌍",
                "tags": ["考证", "语言", "进阶"],
                "author_name": "吴同学",
                "view_count": 543,
                "is_hot": 0,
                "preview_days": 3,
                "price": "68",
                "content": "雅思快速提分的方法和技巧。听说读写全面突破策略。",
                "summary": "雅思从5.5到7.5",
                "status": 1
            },
            {
                "title": "2000小时UI转前端开发",
                "category": "技能学习",
                "duration": "2000h",
                "icon": "💻",
                "tags": ["技能学习", "转行", "前端"],
                "author_name": "郑开发",
                "view_count": 721,
                "is_hot": 0,
                "preview_days": 3,
                "price": "88",
                "content": "从UI设计转前端开发的学习路线。JavaScript、框架学习经验分享。",
                "summary": "UI转前端开发",
                "status": 1
            }
        ]
        
        created_cases = []
        for i, case_data in enumerate(cases_data, 1):
            case = SuccessCase(
                user_id=1,  # 关联到测试用户
                **case_data,
                publish_time=datetime.now()
            )
            db.add(case)
            db.flush()
            created_cases.append(case)
            
            hot_marker = "🔥" if case_data["is_hot"] else "  "
            print(f"   {hot_marker} ✓ {case.title} ({case.duration}, {case.view_count}浏览)")
        
        db.commit()
        print(f"\n✅ 共创建 {len(created_cases)} 个成功案例\n")
        
        # 统计信息
        print("📊 数据统计:")
        total_cases = db.query(SuccessCase).count()
        hot_cases = db.query(SuccessCase).filter(SuccessCase.is_hot == 1).count()
        categories = db.query(SuccessCase.category).distinct().all()
        
        print(f"   • 总案例数: {total_cases}")
        print(f"   • 热门案例: {hot_cases}")
        print(f"   • 分类数: {len(categories)}")
        print(f"   • 分类: {', '.join([c[0] for c in categories])}")
        
        print("\n✅ 成功案例数据添加成功！")
        print("\n🌐 现在可以在前端查看:")
        print("   • 打开 http://localhost:3000/success")
        print("   • 查看热门推荐（4个热门案例）")
        print("   • 查看案例列表（12个案例）")
        print("   • 测试筛选功能\n")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_success_cases() 