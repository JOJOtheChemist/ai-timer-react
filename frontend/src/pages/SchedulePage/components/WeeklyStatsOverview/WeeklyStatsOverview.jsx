import React from 'react';
import './WeeklyStatsOverview.css';

const WeeklyStatsOverview = ({ stats, onShowFullStats }) => {
  return (
    <div className="weekly-stats-overview">
      <div className="stats-header">
        <h2 className="stats-title">本周统计</h2>
        <button onClick={onShowFullStats} className="stats-more-btn">
          查看完整统计 <i className="fa fa-angle-right ml-1"></i>
        </button>
      </div>
      
      <div className="stats-cards">
        {stats.map((stat, index) => (
          <div key={index} className="stat-card">
            <div className={`stat-value ${stat.color}`}>{stat.value}</div>
            <div className="stat-label">{stat.title}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WeeklyStatsOverview; 