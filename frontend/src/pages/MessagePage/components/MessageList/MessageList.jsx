import React from 'react';
import MessageItem from '../MessageItem/MessageItem';
import './MessageList.css';

const MessageList = ({ 
  activeTab, 
  tutorMessages, 
  privateMessages, 
  systemMessages,
  onMessageClick,
  formatTime 
}) => {
  // 根据activeTab选择对应的消息列表
  const getMessages = () => {
    switch (activeTab) {
      case 'tutor':
        return { messages: tutorMessages, type: 'tutor' };
      case 'private':
        return { messages: privateMessages, type: 'private' };
      case 'system':
        return { messages: systemMessages, type: 'system' };
      default:
        return { messages: [], type: '' };
    }
  };

  const { messages, type } = getMessages();

  const renderEmptyState = () => {
    const emptyMessages = {
      tutor: '暂无导师反馈',
      private: '暂无私信',
      system: '暂无系统通知'
    };

    return (
      <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
        {emptyMessages[activeTab]}
      </div>
    );
  };

  return (
    <div className={`msg-container ${activeTab ? 'active' : ''}`}>
      {/* 私信页特有的搜索栏 */}
      {activeTab === 'private' && (
        <div className="search-bar">
          <i>🔍</i>
          <input type="text" placeholder="搜索联系人" />
        </div>
      )}
      
      {/* 消息列表 */}
      <div className="msg-list">
        {messages.length > 0 ? (
          messages.map(msg => (
            <MessageItem
              key={msg.id}
              message={msg}
              type={type}
              onClick={onMessageClick}
              formatTime={formatTime}
            />
          ))
        ) : (
          renderEmptyState()
        )}
      </div>
    </div>
  );
};

export default MessageList; 