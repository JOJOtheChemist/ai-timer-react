import React from 'react';
import './ChatTopNav.css';

const ChatTopNav = ({ onBack, onMinimize }) => {
  return (
    <div className="chat-top-nav">
      <div className="back-btn" onClick={onBack}>←</div>
      <div className="title">AI时间助手</div>
      <div className="min-btn" onClick={onMinimize}>—</div>
    </div>
  );
};

export default ChatTopNav; 