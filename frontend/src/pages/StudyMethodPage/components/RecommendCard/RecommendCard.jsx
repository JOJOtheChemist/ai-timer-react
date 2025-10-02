import React from 'react';
import './RecommendCard.css';

const RecommendCard = ({ recommendation, onUse, onChange }) => {
  return (
    <div className="ai-recommend">
      <div className="ai-icon">🤖</div>
      <div className="ai-content">
        <div className="ai-title">{recommendation.title}</div>
        <div className="ai-desc">{recommendation.desc}</div>
        <div className="ai-actions">
          <button 
            className="ai-btn primary"
            onClick={onUse}
          >
            立即使用
          </button>
          <button 
            className="ai-btn secondary"
            onClick={onChange}
          >
            换一个
          </button>
        </div>
      </div>
    </div>
  );
};

export default RecommendCard; 