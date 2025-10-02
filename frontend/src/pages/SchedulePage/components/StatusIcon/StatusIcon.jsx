import React from 'react';

const StatusIcon = ({ status }) => {
  const getIcon = () => {
    const iconMap = {
      'completed': 'fa-check-circle',
      'in-progress': 'fa-clock-o',
      'pending': 'fa-hourglass-half',
      'empty': 'fa-plus-circle'
    };
    return iconMap[status] || 'fa-circle-o';
  };

  const getColor = () => {
    const colorMap = {
      'completed': 'text-green-500',
      'in-progress': 'text-blue-500',
      'pending': 'text-gray-400',
      'empty': 'text-gray-300'
    };
    return colorMap[status] || 'text-gray-400';
  };

  return (
    <i className={`fa ${getIcon()} ${getColor()}`}></i>
  );
};

export default StatusIcon; 