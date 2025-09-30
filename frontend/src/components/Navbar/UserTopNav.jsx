import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './NavbarCommon.css';

const UserTopNav = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { id: 'main-schedule', label: '我的时间表', path: '/main-schedule' },
    { id: 'success', label: '上岸时间表', path: '/success' },
    { id: 'tutor', label: '导师推荐', path: '/tutor' },
    { id: 'study-method', label: '学习方法', path: '/study-method' }
  ];

  const handleTabClick = (tab) => {
    navigate(tab.path);
  };

  const isActive = (path) => {
    if (path === '/main-schedule') {
      return location.pathname === '/' || location.pathname === '/main-schedule';
    }
    return location.pathname === path;
  };

  return (
    <header className="user-top-nav sticky top-0 z-40 bg-white shadow-sm">
      <div className="nav-header">
        <h1 className="nav-title">智能时间管理</h1>
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

export default UserTopNav;
