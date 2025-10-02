import React from 'react';
import './TaskSearch.css';

const TaskSearch = ({ searchText, onSearchChange }) => {
  return (
    <div className="task-search">
      <div className="search-input-wrapper">
        <input 
          type="text" 
          placeholder="搜索任务..." 
          value={searchText || ''}
          onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
          className="search-input"
        />
        <i className="fa fa-search search-icon"></i>
      </div>
      <button className="filter-btn">
        <i className="fa fa-filter"></i>
      </button>
    </div>
  );
};

export default TaskSearch; 