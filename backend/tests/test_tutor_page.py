import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from services.tutor.tutor_service import TutorService
from services.tutor.tutor_detail_service import TutorDetailService
from services.user.user_asset_service import UserAssetService
from services.user.user_relation_service import UserRelationService
from crud.tutor.crud_tutor import CRUDTutor
from crud.tutor.crud_tutor_review import CRUDTutorReview
from crud.tutor.crud_tutor_service_order import CRUDTutorServiceOrder
from models.schemas.tutor import TutorFilterParams


class TestTutorService:
    """导师服务测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.mock_db = Mock(spec=Session)
        self.tutor_service = TutorService(self.mock_db)
        self.mock_crud_tutor = Mock(spec=CRUDTutor)
        self.tutor_service.crud_tutor = self.mock_crud_tutor

    @pytest.mark.asyncio
    async def test_get_tutor_list_success(self):
        """测试获取导师列表成功"""
        # 准备测试数据
        filters = TutorFilterParams(
            tutor_type="学术导师",
            domain="数学",
            price_range="100-500"
        )
        
        mock_tutors = [
            Mock(
                id=1,
                name="张老师",
                avatar="avatar1.jpg",
                title="高级数学导师",
                tutor_type="学术导师",
                domains="数学,物理",
                experience_years=5,
                rating=4.8,
                review_count=100,
                student_count=200,
                price_range="100-500",
                is_verified=True,
                is_online=True,
                response_rate=0.95,
                service_summary="专业数学辅导",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        self.mock_crud_tutor.get_multi_by_filters = AsyncMock(return_value=mock_tutors)
        
        # 执行测试
        result = await self.tutor_service.get_tutor_list(
            filters=filters,
            sort_by="rating",
            page=1,
            page_size=20
        )
        
        # 验证结果
        assert len(result) == 1
        assert result[0].name == "张老师"
        assert result[0].tutor_type == "学术导师"
        self.mock_crud_tutor.get_multi_by_filters.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_tutors_success(self):
        """测试搜索导师成功"""
        # 准备测试数据
        keyword = "数学"
        mock_tutors = [
            Mock(
                id=1,
                name="数学王老师",
                avatar="avatar1.jpg",
                title="数学专家",
                tutor_type="学术导师",
                domains="数学",
                rating=4.9,
                review_count=150,
                price_range="200-800",
                is_verified=True
            )
        ]
        
        self.mock_crud_tutor.search_by_keyword = AsyncMock(return_value=mock_tutors)
        
        # 执行测试
        result = await self.tutor_service.search_tutors(
            keyword=keyword,
            page=1,
            page_size=20
        )
        
        # 验证结果
        assert len(result) == 1
        assert "数学" in result[0].name
        self.mock_crud_tutor.search_by_keyword.assert_called_once_with(
            self.mock_db,
            keyword=keyword,
            skip=0,
            limit=20
        )

    @pytest.mark.asyncio
    async def test_get_tutor_service_price_success(self):
        """测试获取服务价格成功"""
        # 准备测试数据
        tutor_id = 1
        service_id = 1
        mock_service = Mock(
            id=1,
            tutor_id=1,
            name="一对一数学辅导",
            price=200.0,
            currency="CNY",
            is_available=True
        )
        
        self.mock_crud_tutor.get_service_by_id = AsyncMock(return_value=mock_service)
        
        # 执行测试
        result = await self.tutor_service.get_tutor_service_price(tutor_id, service_id)
        
        # 验证结果
        assert result is not None
        assert result["id"] == 1
        assert result["name"] == "一对一数学辅导"
        assert result["price"] == 200.0
        assert result["is_available"] == True

    @pytest.mark.asyncio
    async def test_get_tutor_service_price_invalid_tutor(self):
        """测试获取服务价格-导师不匹配"""
        # 准备测试数据
        tutor_id = 1
        service_id = 1
        mock_service = Mock(
            id=1,
            tutor_id=2,  # 不匹配的导师ID
            name="一对一数学辅导",
            price=200.0
        )
        
        self.mock_crud_tutor.get_service_by_id = AsyncMock(return_value=mock_service)
        
        # 执行测试
        result = await self.tutor_service.get_tutor_service_price(tutor_id, service_id)
        
        # 验证结果
        assert result is None


class TestTutorDetailService:
    """导师详情服务测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.mock_db = Mock(spec=Session)
        self.tutor_detail_service = TutorDetailService(self.mock_db)
        self.mock_crud_tutor = Mock(spec=CRUDTutor)
        self.mock_crud_tutor_review = Mock(spec=CRUDTutorReview)
        self.tutor_detail_service.crud_tutor = self.mock_crud_tutor
        self.tutor_detail_service.crud_tutor_review = self.mock_crud_tutor_review

    @pytest.mark.asyncio
    async def test_get_tutor_detail_success(self):
        """测试获取导师详情成功"""
        # 准备测试数据
        tutor_id = 1
        user_id = 1
        
        mock_tutor = Mock(
            id=1,
            name="张老师",
            avatar="avatar1.jpg",
            title="高级数学导师",
            bio="专业数学教师",
            tutor_type="学术导师",
            domains="数学,物理",
            experience_years=5,
            education_background="清华大学数学系",
            certifications="高级教师资格证",
            rating=4.8,
            review_count=100,
            student_count=200,
            success_rate=0.85,
            response_rate=0.95,
            response_time="2小时内",
            is_verified=True,
            is_online=True,
            is_active=True,
            is_banned=False,
            last_active=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.mock_crud_tutor.get_by_id_with_relations = AsyncMock(return_value=mock_tutor)
        self.tutor_detail_service.get_tutor_services = AsyncMock(return_value=[])
        self.tutor_detail_service.get_tutor_reviews = AsyncMock(return_value=[])
        self.tutor_detail_service.get_tutor_metrics = AsyncMock(return_value={})
        self.tutor_detail_service._check_user_followed = AsyncMock(return_value=False)
        
        # 执行测试
        result = await self.tutor_detail_service.get_tutor_detail(tutor_id, user_id)
        
        # 验证结果
        assert result is not None
        assert result.id == 1
        assert result.name == "张老师"
        assert result.is_followed == False

    @pytest.mark.asyncio
    async def test_record_tutor_view_success(self):
        """测试记录导师浏览成功"""
        # 准备测试数据
        tutor_id = 1
        user_id = 1
        
        self.mock_crud_tutor.check_user_viewed_today = AsyncMock(return_value=False)
        self.mock_crud_tutor.increment_views = AsyncMock(return_value=True)
        self.mock_crud_tutor.create_view_record = AsyncMock(return_value=True)
        
        # 执行测试
        result = await self.tutor_detail_service.record_tutor_view(tutor_id, user_id)
        
        # 验证结果
        assert result == True
        self.mock_crud_tutor.check_user_viewed_today.assert_called_once()
        self.mock_crud_tutor.increment_views.assert_called_once()
        self.mock_crud_tutor.create_view_record.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_tutor_view_already_viewed(self):
        """测试记录导师浏览-已浏览过"""
        # 准备测试数据
        tutor_id = 1
        user_id = 1
        
        self.mock_crud_tutor.check_user_viewed_today = AsyncMock(return_value=True)
        
        # 执行测试
        result = await self.tutor_detail_service.record_tutor_view(tutor_id, user_id)
        
        # 验证结果
        assert result == True
        self.mock_crud_tutor.check_user_viewed_today.assert_called_once()
        # 不应该调用增加浏览次数和创建记录
        self.mock_crud_tutor.increment_views.assert_not_called()
        self.mock_crud_tutor.create_view_record.assert_not_called()


class TestUserAssetServiceTutorExtension:
    """用户资产服务导师扩展测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.mock_db = Mock(spec=Session)
        self.user_asset_service = UserAssetService(self.mock_db)
        self.mock_tutor_service = Mock()
        self.mock_crud_user_asset = Mock()
        self.mock_crud_tutor_service_order = Mock()
        
        self.user_asset_service.tutor_service = self.mock_tutor_service
        self.user_asset_service.crud_user_asset = self.mock_crud_user_asset
        self.user_asset_service.crud_tutor_service_order = self.mock_crud_tutor_service_order

    @pytest.mark.asyncio
    async def test_purchase_tutor_service_success(self):
        """测试购买导师服务成功"""
        # 准备测试数据
        user_id = 1
        tutor_id = 1
        service_id = 1
        
        mock_service_price = {
            "id": 1,
            "name": "一对一数学辅导",
            "price": 200.0,
            "currency": "diamonds"
        }
        
        mock_user_asset = Mock(diamond_count=500.0)
        
        self.mock_tutor_service.get_tutor_service_price = AsyncMock(return_value=mock_service_price)
        self.mock_crud_user_asset.get_asset_by_user_id.return_value = mock_user_asset
        self.mock_crud_user_asset.deduct_diamonds.return_value = True
        self.mock_crud_tutor_service_order.create_order = AsyncMock(return_value="ORDER_123")
        
        # 执行测试
        result = await self.user_asset_service.purchase_tutor_service(user_id, tutor_id, service_id)
        
        # 验证结果
        assert result is not None
        assert result.order_id == "ORDER_123"
        assert result.service_name == "一对一数学辅导"
        assert result.amount == 200.0
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_purchase_tutor_service_insufficient_balance(self):
        """测试购买导师服务-余额不足"""
        # 准备测试数据
        user_id = 1
        tutor_id = 1
        service_id = 1
        
        mock_service_price = {
            "id": 1,
            "name": "一对一数学辅导",
            "price": 200.0,
            "currency": "diamonds"
        }
        
        mock_user_asset = Mock(diamond_count=100.0)  # 余额不足
        
        self.mock_tutor_service.get_tutor_service_price = AsyncMock(return_value=mock_service_price)
        self.mock_crud_user_asset.get_asset_by_user_id.return_value = mock_user_asset
        
        # 执行测试并验证异常
        with pytest.raises(Exception) as exc_info:
            await self.user_asset_service.purchase_tutor_service(user_id, tutor_id, service_id)
        
        assert "钻石余额不足" in str(exc_info.value)


class TestUserRelationServiceTutorExtension:
    """用户关系服务导师扩展测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.mock_db = Mock(spec=Session)
        self.user_relation_service = UserRelationService(self.mock_db)
        self.mock_tutor_service = Mock()
        self.mock_crud_user_relation = Mock()
        self.mock_crud_user_message = Mock()
        
        self.user_relation_service.tutor_service = self.mock_tutor_service
        self.user_relation_service.crud_user_relation = self.mock_crud_user_relation
        self.user_relation_service.crud_user_message = self.mock_crud_user_message

    @pytest.mark.asyncio
    async def test_follow_tutor_success(self):
        """测试关注导师成功"""
        # 准备测试数据
        user_id = 1
        tutor_id = 1
        
        mock_relation = Mock(created_at=datetime.now())
        
        self.mock_tutor_service.check_tutor_exists = AsyncMock(return_value=True)
        self.mock_crud_user_relation.get_relation.return_value = None  # 未关注
        self.mock_crud_user_relation.create_tutor_follow.return_value = mock_relation
        self.mock_tutor_service.update_tutor_fan_count = AsyncMock(return_value=True)
        
        # 执行测试
        result = await self.user_relation_service.follow_tutor(user_id, tutor_id)
        
        # 验证结果
        assert result.is_followed == True
        assert result.message == "关注成功"
        assert result.follow_time is not None

    @pytest.mark.asyncio
    async def test_follow_tutor_already_followed(self):
        """测试关注导师-已关注"""
        # 准备测试数据
        user_id = 1
        tutor_id = 1
        
        mock_existing_relation = Mock(created_at=datetime.now())
        
        self.mock_tutor_service.check_tutor_exists = AsyncMock(return_value=True)
        self.mock_crud_user_relation.get_relation.return_value = mock_existing_relation
        
        # 执行测试
        result = await self.user_relation_service.follow_tutor(user_id, tutor_id)
        
        # 验证结果
        assert result.is_followed == True
        assert result.message == "已关注此导师"

    @pytest.mark.asyncio
    async def test_send_tutor_message_success(self):
        """测试发送导师私信成功"""
        # 准备测试数据
        user_id = 1
        tutor_id = 1
        content = "您好，我想咨询数学学习问题"
        
        mock_message = Mock(
            id=1,
            sender_id=user_id,
            receiver_id=tutor_id,
            content=content,
            message_type="tutor",
            is_read=False,
            created_at=datetime.now()
        )
        
        self.mock_tutor_service.check_tutor_exists = AsyncMock(return_value=True)
        self.mock_crud_user_message.create_private_message = AsyncMock(return_value=mock_message)
        self.user_relation_service._trigger_message_notification = AsyncMock()
        
        # 执行测试
        result = await self.user_relation_service.send_tutor_message(user_id, tutor_id, content)
        
        # 验证结果
        assert result.id == 1
        assert result.sender_id == user_id
        assert result.receiver_id == tutor_id
        assert result.content == content
        assert result.message_type == "tutor"


class TestTutorPageAPIs:
    """导师页API集成测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        # 这里可以设置测试客户端和模拟数据
        pass

    def test_get_tutors_endpoint(self):
        """测试获取导师列表端点"""
        # 集成测试示例
        # 可以使用TestClient进行端到端测试
        pass

    def test_get_tutor_detail_endpoint(self):
        """测试获取导师详情端点"""
        # 集成测试示例
        pass

    def test_purchase_tutor_service_endpoint(self):
        """测试购买导师服务端点"""
        # 集成测试示例
        pass


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"]) 