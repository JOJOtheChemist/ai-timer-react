import React from 'react';
import './MessageItem.css';

const MessageItem = ({ message, type, onClick, formatTime }) => {
  const isUnread = message.is_unread === 1;
  
  return (
    <div 
      className="msg-item" 
      onClick={() => onClick(message)}
    >
      <div className={`msg-avatar ${type === 'system' ? 'system' : type === 'tutor' ? 'tutor' : ''}`}>
        {message.sender_avatar || '👤'}
      </div>
      <div className="msg-content">
        <div className="msg-header">
          <div className="msg-name">
            {message.sender_name || '系统'}
            {type === 'tutor' && message.tutor_certification && (
              <span className="msg-tag">
                {message.tutor_certification === 'verified' ? '认证导师' : '普通导师'}
              </span>
            )}
          </div>
          <div className="msg-time">{formatTime(message.create_time)}</div>
        </div>
        <div className={`msg-text ${isUnread ? 'highlight' : ''}`}>
          {isUnread && <span className="msg-badge"></span>}
          {message.title || message.content.substring(0, 50)}
          {message.content.length > 50 ? '...' : ''}
        </div>
      </div>
    </div>
  );
};

export default MessageItem; 