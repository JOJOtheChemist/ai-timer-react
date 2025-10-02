import React from 'react';
import './FunctionEntrance.css';

const FunctionEntrance = ({ onEntryClick }) => {
  const entrances = [
    { id: 'schedule', name: '时间表', icon: '📅', className: 'schedule' },
    { id: 'post', name: '动态', icon: '📝', className: 'post' },
    { id: 'more', name: '更多', icon: '🔧', className: 'more' }
  ];

  return (
    <div className="function-entrance-container">
      <div className="section-title">功能入口</div>
      <div className="entry-grid">
        {entrances.map(entrance => (
          <div 
            key={entrance.id}
            className="entry-card" 
            onClick={() => onEntryClick(entrance.name)}
          >
            <div className={`entry-icon ${entrance.className}`}>
              {entrance.icon}
            </div>
            <div className="entry-name">{entrance.name}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FunctionEntrance; 