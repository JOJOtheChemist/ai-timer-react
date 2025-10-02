import React, { useState, useEffect } from 'react';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './PersonalPage.css';
import userService from '../../services/userService';

// 导入子组件
import UserInfoCard from './components/UserInfoCard/UserInfoCard';
import MyDiamonds from './components/MyDiamonds/MyDiamonds';
import MyRelationship from './components/MyRelationship/MyRelationship';
import FunctionEntrance from './components/FunctionEntrance/FunctionEntrance';
import MyBadges from './components/MyBadges/MyBadges';
import BadgeModal from './components/BadgeModal/BadgeModal';

const PersonalPage = () => {
  const [showBadgeModal, setShowBadgeModal] = useState(false);
  const [selectedBadge, setSelectedBadge] = useState(null);
  const USER_ID = 101; // TODO: 从认证系统获取

  // 数据状态
  const [profile, setProfile] = useState(null);
  const [assets, setAssets] = useState(null);
  const [relationStats, setRelationStats] = useState({ tutor_count: 0, fan_count: 0, following_count: 0 });
  const [followedTutors, setFollowedTutors] = useState([]);
  const [recentFans, setRecentFans] = useState([]);
  const [loading, setLoading] = useState(true);

  // 徽章数据（暂时硬编码）
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

  // 加载数据
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [profileData, assetsData, statsData, tutorsData, fansData] = await Promise.all([
        userService.getCurrentUserProfile(USER_ID),
        userService.getUserAssets(USER_ID),
        userService.getRelationStats(USER_ID).catch(() => ({ tutor_count: 0, fan_count: 0, following_count: 0 })),
        userService.getFollowedTutors(USER_ID, 3).catch(() => ({ tutors: [] })),
        userService.getRecentFans(USER_ID, 4).catch(() => ({ fans: [] }))
      ]);
      
      setProfile(profileData);
      setAssets(assetsData);
      setRelationStats(statsData);
      setFollowedTutors(tutorsData.tutors || []);
      setRecentFans(fansData.fans || []);
    } catch (error) {
      console.error('加载数据失败:', error);
      alert('加载数据失败，请刷新页面重试');
    } finally {
      setLoading(false);
    }
  };

  // 事件处理函数
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

  // 加载状态
  if (loading) {
    return (
      <div className="personal-page">
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          加载中...
        </div>
        <BottomNavBar />
      </div>
    );
  }

  return (
    <div className="personal-page">
      {/* 页面内标题栏 */}
      <div className="page-header">
        <div className="edit-btn" onClick={handleEditProfile}>编辑资料</div>
        <div className="page-title">我的主页</div>
        <div style={{ width: '60px' }}></div>
      </div>

      {/* 页面容器 */}
      <div className="container">
        {/* 1. 个人信息卡 */}
        <UserInfoCard profile={profile} onEdit={handleEditProfile} />

        {/* 2. 资产区 */}
        <MyDiamonds assets={assets} onRecharge={handleRecharge} />

        {/* 3. 关系链区 */}
        <MyRelationship 
          relationStats={relationStats}
          followedTutors={followedTutors}
          recentFans={recentFans}
          onManageClick={handleRelationEdit}
          onAvatarClick={handleRelationAvatarClick}
        />

        {/* 4. 核心入口区 */}
        <FunctionEntrance onEntryClick={handleEntryClick} />

        {/* 5. 徽章墙 */}
        <MyBadges 
          onBadgeClick={handleBadgeClick}
          onViewMore={handleBadgeMore}
        />
      </div>

      {/* 徽章详情弹窗 */}
      {showBadgeModal && (
        <BadgeModal badge={selectedBadge} onClose={closeBadgeModal} />
      )}

      <BottomNavBar />
    </div>
  );
};

export default PersonalPage; 