import React from 'react';
import './TaskFilterTabs.css';

const TaskFilterTabs = ({ activeFilter, onFilterClick }) => {
  const filters = [
    { key: '全部', label: '全部', color: 'primary' },
    { key: 'study', label: '学习', icon: 'fa-book', color: 'study' },
    { key: 'life', label: '生活', icon: 'fa-home', color: 'life' },
    { key: 'play', label: '玩乐', icon: 'fa-gamepad', color: 'play' },
    { key: 'work', label: '工作', icon: 'fa-briefcase', color: 'work' }
  ];

  return (
    <div className="task-filter-tabs">
      {filters.map(filter => (
        <button
          key={filter.key}
          onClick={() => onFilterClick(filter.key)}
          className={`filter-tab ${activeFilter === filter.key ? 'active' : ''} ${filter.color}`}
        >
          {filter.icon && <i className={`fa ${filter.icon} mr-1`}></i>}
          {filter.label}
        </button>
      ))}
    </div>
  );
};

export default TaskFilterTabs; 