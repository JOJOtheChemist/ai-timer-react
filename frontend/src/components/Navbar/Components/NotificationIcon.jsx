import React from 'react';

const NotificationIcon = ({ hasNotification = false, onClick }) => {
  return (
    <button className="notification-icon" onClick={onClick}>
      <i className="fa fa-bell text-lg"></i>
      {hasNotification && <span className="notification-dot"></span>}
    </button>
  );
};

export default NotificationIcon;
