import React from 'react';
import './TutorCard.css';

const TutorCard = ({ tutor, onClick }) => {
  return (
    <div 
      className="tutor-card"
      onClick={() => onClick(tutor)}
    >
      <div className="tutor-avatar">{tutor.avatar}</div>
      <div className="tutor-info">
        <div className="tutor-header">
          <div className="tutor-name">{tutor.name}</div>
          <div className={`tutor-tag ${tutor.type}`}>
            {tutor.type === 'certified' ? '认证导师' : '普通导师'}
          </div>
        </div>
        <div className="tutor-domain">{tutor.domain}</div>
        <div className="tutor-metrics">
          <div className={`metric-item ${tutor.metrics.rating >= 97 ? 'highlight' : ''}`}>
            <i>⭐</i> {tutor.metrics.rating}%好评
          </div>
          <div className="metric-item">
            <i>👥</i> {tutor.metrics.students}人指导
          </div>
          <div className={`metric-item ${tutor.metrics.successRate >= 85 ? 'highlight' : ''}`}>
            <i>🎯</i> {tutor.metrics.successRate}%上岸
          </div>
        </div>
        <div className="tutor-services">
          {tutor.services.map((service, index) => (
            <div key={index} className="service-tag">
              {service.name} {service.price}钻
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TutorCard; 