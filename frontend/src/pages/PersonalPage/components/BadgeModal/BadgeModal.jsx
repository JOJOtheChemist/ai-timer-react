import React from 'react';
import './BadgeModal.css';

const BadgeModal = ({ badge, onClose }) => {
  if (!badge) return null;

  return (
    <div 
      className="badge-modal show" 
      onClick={(e) => e.target.className.includes('badge-modal') && onClose()}
    >
      <div className="modal-content">
        <div className="modal-header">
          <div className="modal-title">徽章详情</div>
          <div className="close-modal" onClick={onClose}>×</div>
        </div>
        <div className="badge-detail">
          <div className="badge-detail-content">
            <div className={`badge-detail-icon ${badge.getDate === '未获得' ? 'locked' : ''}`}>
              {badge.icon}
            </div>
            <h3 className="badge-detail-name">{badge.name}</h3>
            <p className="badge-detail-desc">{badge.desc}</p>
            <p className="badge-detail-date">
              {badge.getDate !== '未获得' 
                ? `获得时间: ${badge.getDate}` 
                : '解锁条件: 完成对应学习任务'
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BadgeModal; 