import React from 'react';

const SearchBox = ({ placeholder = "搜索...", value, onChange, className = "" }) => {
  return (
    <div className={`search-box ${className}`}>
      <i className="fa fa-search search-icon"></i>
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className="search-input"
      />
    </div>
  );
};

export default SearchBox;
