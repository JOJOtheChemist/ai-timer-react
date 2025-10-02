import React from 'react';
import './MethodTabs.css';

const MethodTabs = ({ filterOptions, activeFilter, onFilterChange }) => {
  return (
    <div className="filter-tab">
      {filterOptions.map(option => (
        <button
          key={option}
          className={`filter-type ${activeFilter === option ? 'active' : ''} ${option === '导师独创' ? 'highlight' : ''}`}
          onClick={() => onFilterChange(option)}
        >
          {option}
        </button>
      ))}
    </div>
  );
};

export default MethodTabs; 