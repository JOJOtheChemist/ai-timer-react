import React from 'react';
import './MethodCard.css';

const MethodCard = ({ method, onCheckin }) => {
  return (
    <div className="method-card" data-method={method.id}>
      <div className="method-header">
        <div className="method-info">
          <div className="method-name">{method.name}</div>
          <div className="method-meta">
            <span className={method.meta.tutor ? 'tutor-tag' : ''}>
              {method.meta.tutor ? method.meta.tutor : `适用：${method.meta.scope}`}
            </span>
            <span>{method.meta.checkinCount}人打卡</span>
          </div>
        </div>
        <div className={`method-tag ${method.type === 'tutor' ? 'tutor' : ''}`}>
          {method.category}
        </div>
      </div>

      <div className="method-body">
        <div className="method-desc">{method.description}</div>
        <div className="method-steps">
          {method.steps.map((step, index) => (
            <div key={index} className="step-item">{step}</div>
          ))}
        </div>
        <div className="method-scene">
          <i>📍</i> {method.scene}
        </div>
      </div>

      <div className="method-footer">
        <div className="method-stats">
          <div className="stats-item">
            <i>⭐</i> {method.stats.rating}分
          </div>
          <div className="stats-item">
            <i>💬</i> {method.stats.reviews}条评价
          </div>
        </div>
        <button 
          className={`checkin-btn ${method.type === 'tutor' ? 'tutor' : ''}`}
          onClick={() => onCheckin(method)}
        >
          立即打卡
        </button>
      </div>
    </div>
  );
};

export default MethodCard; 