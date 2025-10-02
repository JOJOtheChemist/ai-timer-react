import React from 'react';
import './RecommendCard.css';

const RecommendCard = ({ recommendData, onClick }) => {
  const { icon, name, desc, tag, type } = recommendData;
  
  return (
    <div 
      className="recommend-card" 
      onClick={() => onClick(recommendData)}
    >
      <div className={`recommend-icon icon-${type}`}>
        {icon}
      </div>
      <div className="recommend-info">
        <div className="recommend-name">{name}</div>
        <div className="recommend-desc">{desc}</div>
      </div>
      <div className="recommend-tag">{tag}</div>
    </div>
  );
};

export default RecommendCard; 