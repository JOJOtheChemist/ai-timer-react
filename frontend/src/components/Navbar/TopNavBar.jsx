import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './TopNavBar.css';

const TopNavBar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { id: 'main-schedule', label: '我的时间表', path: '/main-schedule' },
    { id: 'schedule', label: '上岸时间表', path: '/schedule' },
    { id: 'tutor', label: '导师推荐', path: '/tutor' },
    { id: 'challenge', label: '打卡挑战', path: '/challenge' }
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
    <header className="top-nav-bar sticky top-0 z-40 bg-white shadow-sm">
      <div className="flex items-center justify-between px-4 h-14">
        <h1 className="text-lg font-semibold text-primary">智能时间管理</h1>
        <div className="flex items-center gap-3">
          <button className="text-gray-500 hover:text-primary relative">
            <i className="fa fa-search text-lg"></i>
          </button>
          <button className="text-gray-500 hover:text-primary relative">
            <i className="fa fa-bell text-lg"></i>
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-warning rounded-full"></span>
          </button>
        </div>
      </div>

      {/* 顶部菜单栏 */}
      <div className="border-t border-gray-100 overflow-x-auto scrollbar-thin">
        <div className="flex">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`flex-1 py-3 text-sm border-b-2 border-transparent whitespace-nowrap transition-colors ${
                isActive(tab.path)
                  ? 'text-primary border-primary font-medium' 
                  : 'text-gray-500 hover:text-primary'
              }`}
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

export default TopNavBar;
