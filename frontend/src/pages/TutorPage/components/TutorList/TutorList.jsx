import React from 'react';
import TutorCard from '../TutorCard/TutorCard';
import './TutorList.css';

const TutorList = ({ tutors, onTutorClick }) => {
  if (tutors.length === 0) {
    return (
      <div className="tutor-list-empty">
        <div className="empty-icon">🔍</div>
        <div className="empty-text">暂无匹配的导师</div>
        <div className="empty-desc">试试调整筛选条件或搜索关键词</div>
      </div>
    );
  }

  return (
    <div className="tutor-list">
      {tutors.map(tutor => (
        <TutorCard
          key={tutor.id}
          tutor={tutor}
          onClick={onTutorClick}
        />
      ))}
    </div>
  );
};

export default TutorList; 