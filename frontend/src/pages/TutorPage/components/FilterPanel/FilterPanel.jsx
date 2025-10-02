import React from 'react';
import './FilterPanel.css';

const FilterPanel = ({ filterOptions, activeFilters, onFilterChange }) => {
  return (
    <div className="filter-area">
      {/* 导师类型筛选 */}
      <div className="filter-group">
        <div className="group-title">导师类型</div>
        <div className="filter-tags">
          {filterOptions.tutorType.map(option => (
            <div 
              key={option}
              className={`filter-tag ${activeFilters.tutorType.includes(option) ? 'active' : ''} ${option === '认证导师' ? 'highlight' : ''}`}
              onClick={() => onFilterChange('tutorType', option)}
            >
              {option}
            </div>
          ))}
        </div>
      </div>

      {/* 擅长领域筛选 */}
      <div className="filter-group">
        <div className="group-title">擅长领域</div>
        <div className="filter-tags">
          {filterOptions.domain.map(option => (
            <div 
              key={option}
              className={`filter-tag ${activeFilters.domain.includes(option) ? 'active' : ''}`}
              onClick={() => onFilterChange('domain', option)}
            >
              {option}
            </div>
          ))}
        </div>
      </div>

      {/* 服务数据筛选 */}
      <div className="filter-group">
        <div className="group-title">服务数据</div>
        <div className="filter-tags">
          {filterOptions.serviceData.map(option => (
            <div 
              key={option}
              className={`filter-tag ${activeFilters.serviceData.includes(option) ? 'active' : ''}`}
              onClick={() => onFilterChange('serviceData', option)}
            >
              {option}
            </div>
          ))}
        </div>
      </div>

      {/* 价格筛选 */}
      <div className="filter-group">
        <div className="group-title">服务价格</div>
        <div className="filter-tags">
          {filterOptions.priceRange.map(option => (
            <div 
              key={option}
              className={`filter-tag ${activeFilters.priceRange.includes(option) ? 'active' : ''}`}
              onClick={() => onFilterChange('priceRange', option)}
            >
              {option}
            </div>
          ))}
          <div 
            className="filter-tag reset"
            onClick={() => onFilterChange('priceRange', '重置筛选')}
          >
            重置筛选
          </div>
        </div>
      </div>
    </div>
  );
};

export default FilterPanel; 