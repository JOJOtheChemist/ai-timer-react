import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './NavbarCommon.css';

const AdminTopNav = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { id: 'dashboard', label: '仪表盘', path: '/admin/dashboard' },
    { id: 'users', label: '用户管理', path: '/admin/users' },
    { id: 'content', label: '内容管理', path: '/admin/content' },
    { id: 'settings', label: '系统设置', path: '/admin/settings' }
  ];

  const handleTabClick = (tab) => {
    navigate(tab.path);
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <header className="admin-top-nav sticky top-0 z-40 bg-white shadow-sm">
      <div className="nav-header">
        <h1 className="nav-title">管理后台</h1>
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

export default AdminTopNav;
