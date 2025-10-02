import React from 'react';
import './MessageHeader.css';

const MessageHeader = ({ onBack, onSettingClick }) => {
  return (
    <div className="nav-top">
      <div className="back-btn" onClick={onBack}>←</div>
      <div className="title">消息中心</div>
      <div className="setting-btn" onClick={onSettingClick}>⚙️</div>
    </div>
  );
};

export default MessageHeader; 