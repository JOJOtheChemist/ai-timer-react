import React from 'react';

const StatCard = ({ title, value, colorClass = 'text-primary' }) => {
  return (
    <div className="bg-gray-50 rounded-lg p-2 stat-card">
      <div className="text-xs text-gray-500">{title}</div>
      <div className={`text-lg font-bold ${colorClass}`}>{value}</div>
    </div>
  );
};

export default StatCard; 