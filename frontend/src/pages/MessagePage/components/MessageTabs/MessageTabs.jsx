import React from 'react';
import './MessageTabs.css';

const MessageTabs = ({ activeTab, onTabChange, unreadStats }) => {
  const tabs = [
    { id: 'tutor', label: '导师反馈', unreadKey: 'tutor_count' },
    { id: 'private', label: '私信', unreadKey: 'private_count' },
    { id: 'system', label: '系统通知', unreadKey: 'system_count' }
  ];

  return (
    <div className="tab-container">
      {tabs.map(tab => (
        <button 
          key={tab.id}
          className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
          {unreadStats[tab.unreadKey] > 0 && (
            <span className="badge">{unreadStats[tab.unreadKey]}</span>
          )}
        </button>
      ))}
    </div>
  );
};

export default MessageTabs; 