# MomentsPage 前后端集成指南

## 📋 完成的工作

### 1. 后端准备
- ✅ 修复 MomentAttachment 模型字段名匹配数据库表结构
- ✅ 添加 7 条测试数据（1 条广告 + 3 条动态 + 3 条干货）
- ✅ API 能正确返回动态列表

### 2. 前端服务层
- ✅ 创建 `momentService.js`
  - getMomentList - 获取动态列表
  - searchMoments - 搜索
  - getPopularTags - 获取热门标签
  - publishDynamic - 发布动态
  - publishDryGoods - 发布干货
  - toggleLike - 点赞/取消
  - getComments - 获取评论
  - submitComment - 提交评论
  - shareMoment - 分享
  - toggleBookmark - 收藏

## 🔄 集成步骤

### 步骤 1: 修改 MomentsPage.jsx 导入

```javascript
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './MomentsPage.css';
import momentService from '../../services/momentService';
```

### 步骤 2: 添加状态管理

```javascript
const [dynamicPosts, setDynamicPosts] = useState([]);
const [dryGoodsPosts, setDryGoodsPosts] = useState([]);
const [loading, setLoading] = useState(true);
const USER_ID = 1; // TODO: 从认证系统获取
```

### 步骤 3: 添加数据加载函数

```javascript
const loadPosts = async (type = 'dynamic') => {
  try {
    setLoading(true);
    const params = {
      moment_type: type,
      user_id: USER_ID,
      page: 1,
      page_size: 20
    };
    
    // 添加筛选条件
    if (selectedTags.length > 0 && !selectedTags.includes('全部标签')) {
      params.tags = selectedTags;
    }
    if (selectedTime.length > 0 && !selectedTime.includes('全部时间')) {
      // 转换时间范围
      const timeMap = {
        '今日': 'today',
        '本周': 'week',
        '本月': 'month'
      };
      params.time_range = timeMap[selectedTime[0]] || 'all';
    }
    if (selectedHot.length > 0 && selectedHot[0] !== '推荐') {
      const hotMap = {
        '最新': 'latest',
        '最热': 'hot'
      };
      params.hot_type = hotMap[selectedHot[0]];
    }
    
    const response = await momentService.getMomentList(params);
    
    // 转换数据格式
    const formatted = response.moments.map(moment => ({
      id: moment.id,
      type: moment.type === 2 ? 'ad' : (moment.type === 1 ? 'dryGoods' : 'dynamic'),
      user: {
        name: moment.user?.name || '用户',
        avatar: moment.user?.avatar || '👤'
      },
      time: moment.time_ago || '刚刚',
      title: moment.title,
      content: moment.content,
      tags: moment.tags || [],
      stats: {
        likes: moment.stats?.likes || 0,
        comments: moment.stats?.comments || 0,
        shares: moment.stats?.shares || 0
      },
      image: moment.image_url,
      isAd: moment.type === 2,
      adInfo: moment.ad_info
    }));
    
    if (type === 'dynamic') {
      setDynamicPosts(formatted);
    } else {
      setDryGoodsPosts(formatted);
    }
  } catch (error) {
    console.error('加载动态失败:', error);
  } finally {
    setLoading(false);
  }
};
```

### 步骤 4: 添加 useEffect 钩子

```javascript
// 初始加载
useEffect(() => {
  loadPosts(activeMode === 'dynamic' ? 'dynamic' : 'dryGoods');
}, []);

// 模式切换时重新加载
useEffect(() => {
  loadPosts(activeMode === 'dynamic' ? 'dynamic' : 'dryGoods');
}, [activeMode]);

// 筛选条件变化时重新加载
useEffect(() => {
  if (!loading) {
    loadPosts(activeMode === 'dynamic' ? 'dynamic' : 'dryGoods');
  }
}, [selectedTags, selectedTime, selectedHot]);
```

### 步骤 5: 更新互动函数

```javascript
const handleLike = async (postId) => {
  try {
    await momentService.toggleLike(postId);
    // 重新加载数据
    await loadPosts(activeMode === 'dynamic' ? 'dynamic' : 'dryGoods');
  } catch (error) {
    console.error('点赞失败:', error);
  }
};

const handleComment = async (postId, content) => {
  try {
    await momentService.submitComment(postId, content);
    // 重新加载数据
    await loadPosts(activeMode === 'dynamic' ? 'dynamic' : 'dryGoods');
  } catch (error) {
    console.error('评论失败:', error);
  }
};

const handleShare = async (postId) => {
  try {
    await momentService.shareMoment(postId);
    alert('分享成功！');
  } catch (error) {
    console.error('分享失败:', error);
  }
};
```

### 步骤 6: 更新发布函数

```javascript
const handlePublish = async () => {
  try {
    const postData = {
      content: postContent.trim(),
      tags: postTags.split(/[,，\s]+/).filter(t => t.trim()),
      image_url: postImage || null
    };
    
    if (postMode === 'dynamic') {
      await momentService.publishDynamic(postData);
    } else {
      postData.title = postTitle.trim();
      await momentService.publishDryGoods(postData);
    }
    
    alert('发布成功！');
    closePostModal();
    // 重新加载
    await loadPosts(activeMode === 'dynamic' ? 'dynamic' : 'dryGoods');
  } catch (error) {
    console.error('发布失败:', error);
    alert('发布失败，请稍后重试');
  }
};
```

### 步骤 7: 添加加载状态 UI

```javascript
if (loading) {
  return (
    <div className="moments-page">
      <div className="loading-container">
        <div className="loading-spinner">加载中...</div>
      </div>
      <BottomNavBar />
    </div>
  );
}
```

## 📊 数据格式映射

### 后端 API 返回格式
```json
{
  "moments": [
    {
      "id": 1,
      "type": 0,
      "title": null,
      "content": "...",
      "tags": ["标签1", "标签2"],
      "user": {
        "name": "用户名",
        "avatar": "头像"
      },
      "stats": {
        "likes": 12,
        "comments": 3,
        "shares": 0
      },
      "image_url": "...",
      "time_ago": "10分钟前"
    }
  ],
  "total": 7,
  "page": 1,
  "page_size": 10
}
```

### 前端组件期望格式
```javascript
{
  id: 1,
  type: 'dynamic',  // 'dynamic' | 'dryGoods' | 'ad'
  user: {
    name: "用户名",
    avatar: "头像"
  },
  time: "10分钟前",
  title: "标题（干货专用）",
  content: "内容",
  tags: ["标签1", "标签2"],
  stats: {
    likes: 12,
    comments: 3,
    shares: 0
  },
  image: "图片URL",
  isAd: false,
  adInfo: "广告信息（广告专用）"
}
```

## ✅ 测试步骤

1. 访问 http://localhost:3000/moments
2. 检查动态列表显示（应该显示 4 条：1 个广告 + 3 个动态）
3. 切换到"干货"模式（应该显示 3 条干货）
4. 测试筛选功能
5. 测试搜索功能
6. 测试点赞/评论/分享功能
7. 测试发布功能

## 🎯 预期效果

- ✅ 显示真实的动态/干货数据
- ✅ 置顶广告显示在最前面
- ✅ 筛选和搜索正常工作
- ✅ 点赞/评论/分享功能正常
- ✅ 发布功能正常
- ✅ 加载状态显示正常 