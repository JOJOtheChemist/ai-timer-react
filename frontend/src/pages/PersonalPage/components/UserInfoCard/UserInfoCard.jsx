import React from 'react';
import './UserInfoCard.css';

const UserInfoCard = ({ profile, onEdit }) => {
  return (
    <div className="profile-card">
      <div className="profile-avatar">
        {profile?.avatar ? (
          <img src={profile.avatar} alt="avatar" style={{width: '100%', height: '100%', borderRadius: '50%'}} />
        ) : '👩'}
      </div>
      <div className="profile-name">{profile?.username || '用户'}</div>
      <div className="profile-meta">
        <span>Goal：{profile?.goal || '暂无目标'}</span>
        <span>Major：{profile?.major || '暂无专业'}</span>
      </div>
      <div className="profile-stats">
        <div className="stat-item">
          <div className="stat-value">{profile?.total_study_hours || '0'}h</div>
          <div className="stat-label">总学习时长</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">{profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : '-'}</div>
          <div className="stat-label">加入日期</div>
        </div>
      </div>
    </div>
  );
};

export default UserInfoCard; 