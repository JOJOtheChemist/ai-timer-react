import React from 'react';
import './SortBar.css';

const SortBar = ({ sortOptions, sortBy, onSortChange, tutorCount }) => {
  return (
    <div className="sort-bar">
      <div className="sort-title">找到 {tutorCount} 位导师</div>
      <div className="sort-options">
        {sortOptions.map(option => (
          <div 
            key={option}
            className={`sort-option ${sortBy === option ? 'active' : ''}`}
            onClick={() => onSortChange(option)}
          >
            {option}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SortBar; 