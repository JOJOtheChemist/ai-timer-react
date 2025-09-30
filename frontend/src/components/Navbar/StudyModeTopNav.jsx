import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './NavbarCommon.css';

const StudyModeTopNav = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { id: 'focus', label: '专注模式', path: '/study/focus' },
    { id: 'timer', label: '番茄钟', path: '/study/timer' },
    { id: 'notes', label: '学习笔记', path: '/study/notes' },
    { id: 'progress', label: '学习进度', path: '/study/progress' }
  ];

  const handleTabClick = (tab) => {
    navigate(tab.path);
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <header className="study-top-nav sticky top-0 z-40 bg-white shadow-sm">
      <div className="nav-header">
        <h1 className="nav-title">学习模式</h1>
        <div className="nav-actions">
          <button className="nav-action-btn">
            <i className="fa fa-search text-lg"></i>
          </button>
          <button className="nav-action-btn relative">
            <i className="fa fa-bell text-lg"></i>
            <span className="notification-dot"></span>
          </button>
        </div>
      </div>

      {/* 顶部菜单栏 */}
      <div className="nav-tabs-container">
        <div className="nav-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`nav-tab ${isActive(tab.path) ? 'active' : ''}`}
              onClick={() => handleTabClick(tab)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
    </header>
  );
};

export default StudyModeTopNav;
