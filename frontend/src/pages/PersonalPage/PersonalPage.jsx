import React, { useState } from 'react';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './PersonalPage.css';

const PersonalPage = () => {
  const [showBadgeModal, setShowBadgeModal] = useState(false);
  const [selectedBadge, setSelectedBadge] = useState(null);

  // 徽章数据
  const badgeData = {
    1: { name: "坚持之星", desc: "连续7天完成学习计划打卡", getDate: "2024-07-10", icon: "🔥" },
    2: { name: "复习王者", desc: "连续14天完成复习任务，复习频率达到80%以上", getDate: "2024-07-05", icon: "📚" },
    3: { name: "目标达成", desc: "单周学习时长超过计划时长的120%", getDate: "2024-06-28", icon: "🎯" },
    4: { name: "分享达人", desc: "累计发布5条学习动态，获得20次以上点赞", getDate: "2024-06-15", icon: "👥" },
    5: { name: "首次充值", desc: "完成首次钻石充值，开启导师指导服务", getDate: "2024-06-01", icon: "💎" },
    6: { name: "进步神速", desc: "单周学习时长较上一周增长50%以上", getDate: "2024-05-20", icon: "📈" },
    7: { name: "上岸先锋", desc: "成功上传考研上岸经验案例，通过官方审核", getDate: "未获得", icon: "🎓" },
    8: { name: "学霸认证", desc: "累计学习时长达到3000小时，且周均打卡率90%以上", getDate: "未获得", icon: "🏅" }
  };

  const handleBadgeClick = (badgeId) => {
    setSelectedBadge(badgeData[badgeId]);
    setShowBadgeModal(true);
  };

  const closeBadgeModal = () => {
    setShowBadgeModal(false);
    setSelectedBadge(null);
  };

  const handleEditProfile = () => {
    alert('打开编辑资料页面');
  };

  const handleRecharge = () => {
    alert('打开钻石充值页面');
  };

  const handleRelationEdit = () => {
    alert('打开关系管理页面（完整关注/粉丝列表）');
  };

  const handleRelationAvatarClick = (name, type) => {
    alert(`跳转至${type}「${name}」的个人主页`);
  };

  const handleEntryClick = (name) => {
    alert(`跳转至「${name}」页面`);
  };

  const handleBadgeMore = () => {
    alert('跳转至完整徽章墙页面（展示全部20枚徽章）');
  };

  return (
    <div className="personal-page">
      {/* 页面内标题栏 */}
      <div className="page-header">
        <div className="edit-btn" onClick={handleEditProfile}>编辑资料</div>
        <div className="page-title">我的主页</div>
        <div style={{ width: '60px' }}></div> {/* 占位 */}
      </div>

      {/* 页面容器 */}
      <div className="container">
        {/* 1. 个人信息卡 */}
        <div className="profile-card">
          <div className="profile-avatar">👩</div>
          <div className="profile-name">考研的小艾</div>
          <div className="profile-meta">
            <span>Goal：24考研上岸会计学</span>
            <span>Major：财务管理</span>
          </div>
          <div className="profile-stats">
            <div className="stat-item">
              <div className="stat-value">1286h</div>
              <div className="stat-label">总学习时长</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">2024.03.15</div>
              <div className="stat-label">加入日期</div>
            </div>
          </div>
        </div>

        {/* 2. 资产区 */}
        <div className="asset-section">
          <div>
            <div className="asset-info">
              <div className="asset-icon">💎</div>
              <div className="asset-detail">
                <div className="asset-title">我的钻石</div>
                <div className="asset-value">158</div>
                <div className="consume-record">最近：3天前 购买导师咨询 50钻石</div>
              </div>
            </div>
          </div>
          <button className="recharge-btn" onClick={handleRecharge}>充值</button>
        </div>

        {/* 3. 关系链区（紧凑版） */}
        <div className="relation-section">
          <div className="relation-header">
            <div className="relation-title">我的关系</div>
            <div className="relation-edit" onClick={handleRelationEdit}>管理</div>
          </div>
          <div className="relation-stats">
            <div className="relation-item">
              <div className="relation-value">3</div>
              <div className="relation-label">关注导师</div>
            </div>
            <div className="relation-item">
              <div className="relation-value">0</div>
              <div className="relation-label">我的学员</div>
            </div>
            <div className="relation-item">
              <div className="relation-value">28</div>
              <div className="relation-label">粉丝</div>
            </div>
          </div>
          <div className="relation-categories">
            <div className="relation-category">
              <div className="category-title">关注的导师</div>
              <div className="relation-list">
                <div className="relation-avatar tutor" onClick={() => handleRelationAvatarClick('王老师', '导师')}>
                  王
                  <div className="relation-name">王老师</div>
                </div>
                <div className="relation-avatar tutor" onClick={() => handleRelationAvatarClick('李学姐', '导师')}>
                  李
                  <div className="relation-name">李学姐</div>
                </div>
                <div className="relation-avatar tutor" onClick={() => handleRelationAvatarClick('张导师', '导师')}>
                  张
                  <div className="relation-name">张导师</div>
                </div>
              </div>
            </div>
            <div className="relation-category">
              <div className="category-title">最近粉丝</div>
              <div className="relation-list">
                <div className="relation-avatar fan" onClick={() => handleRelationAvatarClick('小琳', '粉丝')}>
                  琳
                  <div className="relation-name">小琳</div>
                  <div className="relation-tag">新</div>
                </div>
                <div className="relation-avatar fan" onClick={() => handleRelationAvatarClick('阿美', '粉丝')}>
                  美
                  <div className="relation-name">阿美</div>
                </div>
                <div className="relation-avatar fan" onClick={() => handleRelationAvatarClick('小楠', '粉丝')}>
                  楠
                  <div className="relation-name">小楠</div>
                </div>
                <div className="relation-avatar fan" onClick={() => handleRelationAvatarClick('琪琪', '粉丝')}>
                  琪
                  <div className="relation-name">琪琪</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 4. 核心入口区（紧凑网格） */}
        <div className="section-title">功能入口</div>
        <div className="entry-grid">
          {/* 我的时间表 */}
          <div className="entry-card" onClick={() => handleEntryClick('时间表')}>
            <div className="entry-icon schedule">📅</div>
            <div className="entry-name">时间表</div>
          </div>
          {/* 我的动态 */}
          <div className="entry-card" onClick={() => handleEntryClick('动态')}>
            <div className="entry-icon post">📝</div>
            <div className="entry-name">动态</div>
          </div>
          {/* 更多功能 */}
          <div className="entry-card" onClick={() => handleEntryClick('更多')}>
            <div className="entry-icon more">🔧</div>
            <div className="entry-name">更多</div>
          </div>
        </div>

        {/* 5. 徽章墙（完整展示） */}
        <div className="section-title">我的徽章</div>
        <div className="badge-wall">
          <div className="badge-header">
            <div className="badge-title">已获得8枚徽章（共20枚）</div>
            <div className="badge-more" onClick={handleBadgeMore}>查看全部</div>
          </div>
          <div className="badge-grid">
            <div className="badge-item" onClick={() => handleBadgeClick('1')}>
              <div className="badge-icon">🔥</div>
              <div className="badge-name">坚持之星</div>
              <div className="badge-desc">连续打卡7天</div>
            </div>
            <div className="badge-item" onClick={() => handleBadgeClick('2')}>
              <div className="badge-icon">📚</div>
              <div className="badge-name">复习王者</div>
              <div className="badge-desc">复习频率达标</div>
            </div>
            <div className="badge-item" onClick={() => handleBadgeClick('3')}>
              <div className="badge-icon">🎯</div>
              <div className="badge-name">目标达成</div>
              <div className="badge-desc">周时长超计划</div>
            </div>
            <div className="badge-item" onClick={() => handleBadgeClick('4')}>
              <div className="badge-icon">👥</div>
              <div className="badge-name">分享达人</div>
              <div className="badge-desc">发布5条动态</div>
            </div>
            <div className="badge-item" onClick={() => handleBadgeClick('5')}>
              <div className="badge-icon">💎</div>
              <div className="badge-name">首次充值</div>
              <div className="badge-desc">充值任意金额</div>
            </div>
            <div className="badge-item" onClick={() => handleBadgeClick('6')}>
              <div className="badge-icon">📈</div>
              <div className="badge-name">进步神速</div>
              <div className="badge-desc">周时长增50%</div>
            </div>
            <div className="badge-item" onClick={() => handleBadgeClick('7')}>
              <div className="badge-icon locked">🔒</div>
              <div className="badge-name">上岸先锋</div>
              <div className="badge-desc">待解锁</div>
            </div>
            <div className="badge-item" onClick={() => handleBadgeClick('8')}>
              <div className="badge-icon locked">🔒</div>
              <div className="badge-name">学霸认证</div>
              <div className="badge-desc">待解锁</div>
            </div>
          </div>
        </div>
      </div>

      {/* 徽章详情弹窗 */}
      {showBadgeModal && selectedBadge && (
        <div className="badge-modal show" onClick={(e) => e.target.className.includes('badge-modal') && closeBadgeModal()}>
          <div className="modal-content">
            <div className="modal-header">
              <div className="modal-title">徽章详情</div>
              <div className="close-modal" onClick={closeBadgeModal}>×</div>
            </div>
            <div className="badge-detail">
              <div className="badge-detail-content">
                <div className={`badge-detail-icon ${selectedBadge.getDate === '未获得' ? 'locked' : ''}`}>
                  {selectedBadge.icon}
                </div>
                <h3 className="badge-detail-name">{selectedBadge.name}</h3>
                <p className="badge-detail-desc">{selectedBadge.desc}</p>
                <p className="badge-detail-date">
                  {selectedBadge.getDate !== '未获得' 
                    ? `获得时间: ${selectedBadge.getDate}` 
                    : '解锁条件: 完成对应学习任务'
                  }
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      <BottomNavBar />
    </div>
  );
};

export default PersonalPage; 