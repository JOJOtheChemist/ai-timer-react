import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch

from main import app
from core.dependencies import get_db, get_current_user

client = TestClient(app)

# 测试数据
MOCK_USER = {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
}

MOCK_CASE_DATA = {
    "id": 1,
    "title": "考研成功案例",
    "category": "考研",
    "duration": "6个月",
    "author_name": "张三",
    "author_id": 1,
    "views": 100,
    "price": 9.9,
    "currency": "CNY"
}

class TestCaseAPI:
    """案例API测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.mock_db = Mock(spec=Session)
        self.mock_user = MOCK_USER
        
        # 覆盖依赖
        app.dependency_overrides[get_db] = lambda: self.mock_db
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
    
    def teardown_method(self):
        """测试后置清理"""
        app.dependency_overrides.clear()
    
    def test_get_hot_cases(self):
        """测试获取热门案例"""
        with patch('services.case.case_service.CaseService.get_hot_cases') as mock_service:
            mock_service.return_value = [MOCK_CASE_DATA]
            
            response = client.get("/api/v1/cases/hot")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["title"] == "考研成功案例"
    
    def test_get_case_list(self):
        """测试获取案例列表"""
        with patch('services.case.case_service.CaseService.get_filtered_cases') as mock_service:
            mock_service.return_value = [MOCK_CASE_DATA]
            
            response = client.get("/api/v1/cases/", params={
                "category": "考研",
                "page": 1,
                "page_size": 20
            })
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
    
    def test_search_cases(self):
        """测试搜索案例"""
        with patch('services.case.case_service.CaseService.search_cases') as mock_service:
            mock_service.return_value = [MOCK_CASE_DATA]
            
            response = client.get("/api/v1/cases/search", params={
                "keyword": "考研",
                "page": 1,
                "page_size": 20
            })
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
    
    def test_get_case_categories(self):
        """测试获取案例分类"""
        with patch('services.case.case_service.CaseService.get_case_categories') as mock_service:
            mock_service.return_value = ["考研", "公务员", "教师资格证"]
            
            response = client.get("/api/v1/cases/categories")
            
            assert response.status_code == 200
            data = response.json()
            assert "考研" in data
            assert "公务员" in data

class TestCaseDetailAPI:
    """案例详情API测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.mock_db = Mock(spec=Session)
        self.mock_user = MOCK_USER
        
        app.dependency_overrides[get_db] = lambda: self.mock_db
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
    
    def teardown_method(self):
        """测试后置清理"""
        app.dependency_overrides.clear()
    
    def test_get_case_detail(self):
        """测试获取案例详情"""
        mock_detail = {
            **MOCK_CASE_DATA,
            "description": "详细描述",
            "content": "案例内容",
            "has_full_access": True
        }
        
        with patch('services.case.case_detail_service.CaseDetailService.get_case_detail') as mock_service:
            mock_service.return_value = mock_detail
            
            response = client.get("/api/v1/cases/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "考研成功案例"
            assert data["has_full_access"] is True
    
    def test_record_case_view(self):
        """测试记录案例浏览"""
        with patch('services.case.case_detail_service.CaseDetailService.record_case_view') as mock_service:
            mock_service.return_value = True
            
            response = client.post("/api/v1/cases/1/view")
            
            assert response.status_code == 200
            data = response.json()
            assert data["message"] == "浏览记录已更新"
    
    def test_get_related_cases(self):
        """测试获取相关案例"""
        with patch('services.case.case_detail_service.CaseDetailService.get_related_cases') as mock_service:
            mock_service.return_value = [MOCK_CASE_DATA]
            
            response = client.get("/api/v1/cases/1/related")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

class TestCasePermissionAPI:
    """案例权限API测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.mock_db = Mock(spec=Session)
        self.mock_user = MOCK_USER
        
        app.dependency_overrides[get_db] = lambda: self.mock_db
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
    
    def teardown_method(self):
        """测试后置清理"""
        app.dependency_overrides.clear()
    
    def test_get_case_permission(self):
        """测试获取案例权限信息"""
        mock_permission = {
            "case_id": 1,
            "preview_days": 7,
            "price": 9.9,
            "currency": "CNY",
            "has_purchased": False,
            "is_author": False,
            "can_preview": True,
            "purchase_required": True,
            "preview_content_ratio": 0.3
        }
        
        with patch('services.case.case_permission_service.CasePermissionService.get_case_permission') as mock_service:
            mock_service.return_value = mock_permission
            
            response = client.get("/api/v1/cases/1/permission")
            
            assert response.status_code == 200
            data = response.json()
            assert data["case_id"] == 1
            assert data["purchase_required"] is True
    
    def test_purchase_case_access(self):
        """测试购买案例访问权限"""
        mock_purchase_result = {
            "success": True,
            "message": "购买成功",
            "order_id": "CASE_1_1_1234567890",
            "purchase_time": "2023-01-01T00:00:00"
        }
        
        with patch('services.case.case_permission_service.CasePermissionService.purchase_case_access') as mock_service:
            mock_service.return_value = mock_purchase_result
            
            response = client.post("/api/v1/cases/1/purchase", json={
                "payment_method": "diamonds",
                "remark": "测试购买"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "购买成功"
    
    def test_check_case_access_status(self):
        """测试检查案例访问状态"""
        mock_status = {
            "access_type": "preview",
            "can_view_full": False,
            "message": "仅可预览，需购买查看完整内容"
        }
        
        with patch('services.case.case_permission_service.CasePermissionService.check_case_access_status') as mock_service:
            mock_service.return_value = mock_status
            
            response = client.get("/api/v1/cases/1/access-status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["access_type"] == "preview"
            assert data["can_view_full"] is False

class TestUserSimpleInfoAPI:
    """用户简易信息API测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.mock_db = Mock(spec=Session)
        self.mock_user = MOCK_USER
        
        app.dependency_overrides[get_db] = lambda: self.mock_db
        app.dependency_overrides[get_current_user] = lambda: self.mock_user
    
    def teardown_method(self):
        """测试后置清理"""
        app.dependency_overrides.clear()
    
    def test_get_user_simple_info(self):
        """测试获取用户简易信息"""
        mock_simple_info = {
            "id": 1,
            "username": "testuser",
            "nickname": "测试用户",
            "avatar": "http://example.com/avatar.jpg",
            "is_verified": False,
            "created_at": "2023-01-01T00:00:00"
        }
        
        with patch('services.user.user_profile_service.UserProfileService.get_simple_user_info') as mock_service:
            mock_service.return_value = mock_simple_info
            
            response = client.get("/api/v1/users/1/simple-info")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["username"] == "testuser"
            assert data["is_verified"] is False

class TestCaseService:
    """案例服务层测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.mock_db = Mock(spec=Session)
    
    def test_case_service_initialization(self):
        """测试案例服务初始化"""
        from services.case.case_service import CaseService
        
        service = CaseService(self.mock_db)
        assert service.db == self.mock_db
        assert service.crud_case is not None

class TestCaseCRUD:
    """案例CRUD测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.mock_db = Mock(spec=Session)
    
    def test_crud_case_initialization(self):
        """测试案例CRUD初始化"""
        from crud.case.crud_case import CRUDCase
        
        crud = CRUDCase()
        assert crud is not None

# 集成测试
class TestSuccessPageIntegration:
    """成功案例页集成测试"""
    
    def test_full_case_workflow(self):
        """测试完整的案例浏览购买流程"""
        # 这里可以添加端到端的集成测试
        # 1. 获取热门案例
        # 2. 查看案例详情
        # 3. 检查权限
        # 4. 购买案例
        # 5. 再次查看详情（应该有完整访问权限）
        pass

if __name__ == "__main__":
    pytest.main([__file__]) 