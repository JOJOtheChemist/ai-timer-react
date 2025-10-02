# 导师页面集成指南 📚

## ✅ 已完成

### 1. 后端准备
- ✅ API端点已存在：`/api/v1/tutors/`
- ✅ 导师详情API：`/api/v1/tutors/{tutor_id}`
- ✅ 搜索API：`/api/v1/tutors/search`

### 2. 前端服务
- ✅ 已创建 `frontend/src/services/tutorService.js`
- ✅ 包含所有必要的API调用函数

### 3. 测试数据
- ✅ 已添加6位导师到数据库
  - 王英语老师（考研英语）
  - 李数学老师（考研数学）
  - 张政治老师（考研政治）
  - 赵计算机老师（计算机考研）
  - 孙心理学老师（心理学考研）
  - 周法律老师（法律硕士）

### 4. API测试结果
```
✅ GET /api/v1/tutors/?user_id=1 - 返回6位导师
```

## 🔄 需要修改的文件

### `frontend/src/pages/TutorPage/TutorPage.jsx`

#### 1. 导入必要的依赖

```javascript
import React, { useState, useEffect } from 'react';
import tutorService from '../../services/tutorService';
```

#### 2. 添加状态管理

```javascript
const TutorPage = () => {
  // ... existing state
  
  // 新增状态
  const [tutors, setTutors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const USER_ID = 1; // TODO: 从认证系统获取
  
  // ...
};
```

#### 3. 添加数据加载函数

```javascript
// 加载导师列表
const loadTutors = async () => {
  try {
    const response = await tutorService.getTutorList({
      tutor_type: activeFilters.tutorType === '全部' ? null : activeFilters.tutorType,
      domain: activeFilters.domain === '全部' ? null : activeFilters.domain,
      price_range: activeFilters.priceRange === '全部' ? null : activeFilters.priceRange,
      sort_by: sortBy,
      page: 1,
      page_size: 20
    });
    
    // 转换API数据格式
    const formatted = response.map(item => ({
      id: item.id,
      name: item.username || item.name,
      avatar: item.avatar || '👨‍🏫',
      type: item.type === 1 ? 'certified' : 'normal',
      domain: item.domain,
      metrics: {
        rating: item.rating,
        students: item.student_count,
        successRate: item.success_rate
      },
      // ... 其他字段映射
    }));
    
    setTutors(formatted);
    setTotalCount(formatted.length);
  } catch (error) {
    console.error('加载导师列表失败:', error);
  }
};
```

#### 4. 添加搜索函数

```javascript
const handleSearch = async (e) => {
  if (e.key === 'Enter' && searchQuery.trim()) {
    try {
      setLoading(true);
      const response = await tutorService.searchTutors(searchQuery);
      // 转换并设置搜索结果
      const formatted = response.map(item => ({
        // ... 格式化逻辑
      }));
      setTutors(formatted);
    } catch (error) {
      console.error('搜索失败:', error);
    } finally {
      setLoading(false);
    }
  }
};
```

#### 5. 添加useEffect钩子

```javascript
useEffect(() => {
  const loadData = async () => {
    setLoading(true);
    await loadTutors();
    setLoading(false);
  };
  loadData();
}, []);

// 筛选和排序变化时重新加载
useEffect(() => {
  if (!loading) {
    loadTutors();
  }
}, [activeFilters, sortBy]);
```

#### 6. 添加加载状态UI

```javascript
if (loading) {
  return (
    <div className="tutor-page">
      <UserTopNav />
      <main className="tutor-content">
        <div style={{ textAlign: 'center', padding: '100px 20px' }}>
          <div style={{ fontSize: '48px' }}>⏳</div>
          <div>加载中...</div>
        </div>
      </main>
      <BottomNavBar />
    </div>
  );
}
```

## 📊 数据映射关系

| 前端字段 | 后端字段 | 说明 |
|---------|---------|-----|
| `name` | `username` | 导师姓名 |
| `avatar` | `avatar` | 头像 |
| `type` | `type` | 0=普通，1=认证 |
| `domain` | `domain` | 擅长领域 |
| `metrics.rating` | `rating` | 评分（0-100） |
| `metrics.students` | `student_count` | 学生数量 |
| `metrics.successRate` | `success_rate` | 成功率（0-100） |

## 🎯 测试步骤

1. 打开浏览器访问 `http://localhost:3000/tutor`
2. 检查导师列表是否显示（应该有6位导师）
3. 测试搜索功能（输入"数学"）
4. 测试筛选功能
5. 测试排序功能
6. 打开开发者工具查看Network请求

## ⚠️ 注意事项

1. **后端字段差异**：
   - 后端使用 `username` 而不是 `name`
   - 后端使用 `student_count` 而不是 `total_students`
   - 后端使用 `type` (0/1) 而不是 `tutor_type` ("certified"/"normal")

2. **user_id参数**：
   - 所有API调用都需要传递 `user_id` 参数
   - 当前使用固定值 `1`
   - 生产环境需要从认证系统获取

3. **导师详情**：
   - 点击导师卡片时需要调用 `tutorService.getTutorDetail(tutorId)`
   - 返回的数据结构可能与前端硬编码的不完全一致
   - 需要进行数据转换

## 🔧 后续改进

1. **导师评价**：数据库trigger问题需要修复
2. **导师服务**：需要添加服务项数据（时间表点评、1v1规划等）
3. **用户认证**：集成真实的用户认证系统
4. **错误处理**：添加更友好的错误提示

## 📝 完整代码示例

由于TutorPage.jsx文件较大（470行），建议分步骤修改：

1. 先修改导入和状态
2. 再添加数据加载函数
3. 然后添加useEffect
4. 最后添加加载状态UI

参考 `frontend/src/pages/SuccessPage/SuccessPage.jsx` 的修改方式。

## ✅ 验证清单

- [ ] 导师列表正常显示
- [ ] 搜索功能正常工作  
- [ ] 筛选功能正常工作
- [ ] 排序功能正常工作
- [ ] 导师详情可以打开
- [ ] 没有控制台错误
- [ ] Network请求正常

---

**API文档**: 参考 `后端md/topnavbar/TutorPage.md`

**相似实现**: 参考 `SuccessPage` 的集成方式 