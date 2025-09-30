import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './BottomNavBar.css';

const BottomNavBar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { id: 'home', label: '首页', icon: 'fa-home', path: '/main-schedule', color: '#6366f1' },
    { id: 'shop', label: '商城', icon: 'fa-store', path: '/shop', color: '#f59e0b' },
    { id: 'moments', label: '动态', icon: 'fa-heart', path: '/moments', color: '#ef4444' },
    { id: 'messages', label: '消息', icon: 'fa-comment', path: '/messages', color: '#10b981' },
    { id: 'personal', label: '个人', icon: 'fa-user', path: '/personal', color: '#8b5cf6' }
  ];

  const handleNavClick = (item) => {
    navigate(item.path);
  };

  const isActive = (path) => {
    if (path === '/main-schedule') {
      return location.pathname === '/' || location.pathname === '/main-schedule';
    }
    return location.pathname === path;
  };

  return (
    <nav className="bottom-nav-bar">
      {navItems.map(item => (
        <button
          key={item.id}
          className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
          onClick={() => handleNavClick(item)}
          style={{ '--item-color': item.color }}
        >
          <i className={`fa ${item.icon} nav-icon`}></i>
          <span className="nav-label">{item.label}</span>
        </button>
      ))}
    </nav>
  );
};

export default BottomNavBar;
