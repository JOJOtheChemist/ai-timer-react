import React from 'react';
import './MyBadges.css';

const MyBadges = ({ onBadgeClick, onViewMore }) => {
  const badges = [
    { id: '1', icon: '🔥', name: '坚持之星', desc: '连续打卡7天', locked: false },
    { id: '2', icon: '📚', name: '复习王者', desc: '复习频率达标', locked: false },
    { id: '3', icon: '🎯', name: '目标达成', desc: '周时长超计划', locked: false },
    { id: '4', icon: '👥', name: '分享达人', desc: '发布5条动态', locked: false },
    { id: '5', icon: '💎', name: '首次充值', desc: '充值任意金额', locked: false },
    { id: '6', icon: '📈', name: '进步神速', desc: '周时长增50%', locked: false },
    { id: '7', icon: '🔒', name: '上岸先锋', desc: '待解锁', locked: true },
    { id: '8', icon: '🔒', name: '学霸认证', desc: '待解锁', locked: true }
  ];

  const unlockedCount = badges.filter(b => !b.locked).length;

  return (
    <div className="badges-container">
      <div className="section-title">我的徽章</div>
      <div className="badge-wall">
        <div className="badge-header">
          <div className="badge-title">已获得{unlockedCount}枚徽章（共{badges.length}枚）</div>
          <div className="badge-more" onClick={onViewMore}>查看全部</div>
        </div>
        <div className="badge-grid">
          {badges.map(badge => (
            <div 
              key={badge.id}
              className="badge-item" 
              onClick={() => onBadgeClick(badge.id)}
            >
              <div className={`badge-icon ${badge.locked ? 'locked' : ''}`}>
                {badge.icon}
              </div>
              <div className="badge-name">{badge.name}</div>
              <div className="badge-desc">{badge.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MyBadges; 