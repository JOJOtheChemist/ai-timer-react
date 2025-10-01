from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from crud.case.crud_case_detail import CRUDCaseDetail
from crud.case.crud_case import CRUDCase
from models.schemas.case import CaseDetailResponse, CaseListResponse

class CaseDetailService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_case_detail = CRUDCaseDetail()
        self.crud_case = CRUDCase()

    async def get_case_detail(self, case_id: int, user_id: int) -> Optional[CaseDetailResponse]:
        """获取案例详情（含完整描述、时间规划、经验总结等）"""
        try:
            # 获取案例详情
            case_detail = await self.crud_case_detail.get_by_id(self.db, case_id)
            
            if not case_detail:
                return None
            
            # 检查用户访问权限
            has_access = await self._check_user_access(case_id, user_id)
            
            # 根据权限返回不同内容
            if has_access:
                # 完整内容
                content = case_detail.full_content
                time_schedule = case_detail.time_schedule
                experience_summary = case_detail.experience_summary
            else:
                # 预览内容
                content = case_detail.preview_content
                time_schedule = case_detail.preview_schedule
                experience_summary = case_detail.preview_summary
            
            return CaseDetailResponse(
                id=case_detail.id,
                title=case_detail.title,
                author_name=case_detail.author_name,
                author_id=case_detail.author_id,
                category=case_detail.category,
                duration=case_detail.duration,
                tags=case_detail.tags.split(',') if case_detail.tags else [],
                description=case_detail.description,
                content=content,
                time_schedule=time_schedule,
                experience_summary=experience_summary,
                target_exam=case_detail.target_exam,
                initial_score=case_detail.initial_score,
                final_score=case_detail.final_score,
                study_methods=case_detail.study_methods.split(',') if case_detail.study_methods else [],
                resources_used=case_detail.resources_used.split(',') if case_detail.resources_used else [],
                challenges_faced=case_detail.challenges_faced,
                key_insights=case_detail.key_insights,
                price=case_detail.price,
                currency=case_detail.currency,
                views=case_detail.views,
                likes=case_detail.likes,
                is_featured=case_detail.is_featured,
                has_full_access=has_access,
                created_at=case_detail.created_at,
                updated_at=case_detail.updated_at
            )
        except Exception as e:
            raise Exception(f"获取案例详情失败: {str(e)}")

    async def record_case_view(self, case_id: int, user_id: int) -> bool:
        """记录案例浏览次数"""
        try:
            # 检查是否已记录过（防止重复计数）
            today_viewed = await self.crud_case_detail.check_user_viewed_today(
                self.db, case_id, user_id
            )
            
            if not today_viewed:
                # 增加浏览次数
                await self.crud_case.increment_views(self.db, case_id)
                
                # 记录用户浏览历史
                await self.crud_case_detail.create_view_record(
                    self.db, case_id, user_id
                )
            
            return True
        except Exception as e:
            raise Exception(f"记录浏览失败: {str(e)}")

    async def get_related_cases(self, case_id: int, limit: int = 5) -> List[CaseListResponse]:
        """获取相关推荐案例（基于标签、分类等相似度）"""
        try:
            # 获取当前案例信息
            current_case = await self.crud_case_detail.get_by_id(self.db, case_id)
            
            if not current_case:
                return []
            
            # 基于标签和分类查找相关案例
            related_cases = await self.crud_case.get_related_cases(
                self.db,
                category=current_case.category,
                tags=current_case.tags,
                exclude_id=case_id,
                limit=limit
            )
            
            # 转换为响应模型
            result = []
            for case in related_cases:
                result.append(CaseListResponse(
                    id=case.id,
                    title=case.title,
                    tags=case.tags.split(',') if case.tags else [],
                    author_name=case.author_name,
                    author_id=case.author_id,
                    duration=case.duration,
                    category=case.category,
                    price=case.price,
                    currency=case.currency,
                    views=case.views,
                    is_featured=case.is_featured,
                    created_at=case.created_at,
                    updated_at=case.updated_at
                ))
            
            return result
        except Exception as e:
            raise Exception(f"获取相关案例失败: {str(e)}")

    async def _check_user_access(self, case_id: int, user_id: int) -> bool:
        """检查用户是否有完整访问权限"""
        try:
            # 检查是否为案例作者
            case = await self.crud_case_detail.get_by_id(self.db, case_id)
            if case and case.author_id == user_id:
                return True
            
            # 检查是否已购买
            has_purchased = await self.crud_case_detail.check_user_purchased(
                self.db, case_id, user_id
            )
            
            return has_purchased
        except Exception as e:
            raise Exception(f"检查访问权限失败: {str(e)}") 