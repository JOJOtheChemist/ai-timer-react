# StudyMethodPage 前后端集成指南

## 📋 集成步骤

### 1. 安装依赖
- 已创建 `methodService.js` 用于 API 调用

### 2. 修改 StudyMethodPage.jsx

#### 导入依赖
```javascript
import React, { useState, useEffect } from 'react';
import methodService from '../../services/methodService';
```

#### 添加状态管理
```javascript
const [studyMethods, setStudyMethods] = useState([]); // 真实数据
const [loading, setLoading] = useState(true);
const USER_ID = 1; // TODO: 从认证系统获取
```

#### 添加数据加载函数
```javascript
const loadMethods = async () => {
  try {
    setLoading(true);
    const filters = {
      user_id: USER_ID,
      page: 1,
      page_size: 20
    };
    
    // 如果有分类筛选，添加category参数
    if (activeFilter !== '全部方法') {
      // 映射前端筛选到后端category
      const categoryMap = {
        '通用方法': 'common',
        '导师独创': 'tutor'
      };
      filters.category = categoryMap[activeFilter];
    }
    
    const methods = await methodService.getMethodList(filters);
    
    // 转换数据格式以匹配组件期望的格式
    const formatted = methods.map(method => ({
      id: method.id,
      name: method.name,
      category: method.category === 'common' ? '通用方法' : '导师独创',
      type: method.category,
      meta: {
        scope: method.meta.scope || method.type,
        tutor: method.meta.tutor,
        checkinCount: method.meta.checkinCount
      },
      description: method.description,
      steps: method.steps,
      scene: method.scene,
      stats: {
        rating: method.stats.rating,
        reviews: method.stats.reviews
      }
    }));
    
    setStudyMethods(formatted);
  } catch (error) {
    console.error('加载学习方法失败:', error);
  } finally {
    setLoading(false);
  }
};
```

#### 添加 useEffect 钩子
```javascript
// 初始加载
useEffect(() => {
  loadMethods();
}, []);

// 筛选变化时重新加载
useEffect(() => {
  if (!loading) {
    loadMethods();
  }
}, [activeFilter]);
```

#### 更新打卡处理函数
```javascript
const handleCompleteCheckin = async () => {
  try {
    const checkinData = {
      checkin_type: checkinType,
      progress: checkinProgress,
      note: checkinNote.trim()
    };
    
    await methodService.submitCheckin(selectedMethod.id, checkinData, USER_ID);
    
    const note = checkinNote.trim() ? '，心得已保存' : '';
    alert(`打卡成功！已完成${checkinProgress}遍复习${note}，同步至你的个人动态~`);
    
    closeCheckinModal();
    // 重新加载数据以更新打卡人数
    loadMethods();
  } catch (error) {
    console.error('打卡失败:', error);
    alert('打卡失败，请稍后重试');
  }
};
```

#### 添加加载状态UI
```javascript
if (loading) {
  return (
    <div className="study-method-page">
      <UserTopNav />
      <main className="study-method-content">
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '400px',
          fontSize: '18px',
          color: '#666'
        }}>
          加载中...
        </div>
      </main>
      <BottomNavBar />
    </div>
  );
}
```

### 3. 数据格式映射

#### 后端API返回格式
```json
{
  "id": 1,
  "name": "艾宾浩斯复习四步法",
  "category": "common",
  "type": "全学科",
  "meta": {
    "scope": "全学科",
    "checkinCount": 1286,
    "tutor": null
  },
  "description": "...",
  "steps": ["步骤1", "步骤2", ...],
  "scene": "推荐场景：...",
  "stats": {
    "rating": 4.9,
    "reviews": 328
  }
}
```

#### 前端组件期望格式
```javascript
{
  id: 1,
  name: "艾宾浩斯复习四步法",
  category: "通用方法",  // common -> "通用方法", tutor -> "导师独创"
  type: "common",
  meta: {
    scope: "全学科",
    checkinCount: 1286
  },
  description: "...",
  steps: ["...", "...", "...", "..."],
  scene: "推荐场景：...",
  stats: {
    rating: 4.9,
    reviews: 328
  }
}
```

## 🔄 测试步骤

1. 确保后端服务运行中
2. 确保前端服务运行中
3. 访问 http://localhost:3000/study-method
4. 检查是否显示6个学习方法
5. 测试筛选功能（全部方法、通用方法、导师独创）
6. 测试打卡功能

## ✅ 完成标志

- [ ] 页面能显示真实的学习方法数据
- [ ] 筛选功能正常工作
- [ ] 打卡功能正常（可以提交）
- [ ] 打卡人数和评分来自数据库
- [ ] 加载状态显示正常 