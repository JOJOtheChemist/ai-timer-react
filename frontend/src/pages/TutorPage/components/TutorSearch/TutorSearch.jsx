import React from 'react';
import './TutorSearch.css';

const TutorSearch = ({ searchQuery, onSearchChange, onSearch }) => {
  return (
    <div className="search-bar">
      <i className="search-icon">🔍</i>
      <input 
        type="text" 
        placeholder="搜索导师姓名/擅长领域，如「考研英语」「CPA」"
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        onKeyPress={onSearch}
      />
    </div>
  );
};

export default TutorSearch; 