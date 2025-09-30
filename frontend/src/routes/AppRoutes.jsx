import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// 导入页面组件
import SchedulePage from '../pages/SchedulePage/SchedulePage';
import MainSchedulePage from '../pages/SchedulePage/MainSchedulePage';
import PersonalPage from '../pages/PersonalPage/PersonalPage';
import OthersPage from '../pages/OthersPage/OthersPage';
import StudyMethodPage from '../pages/StudyMethodPage/StudyMethodPage';
import TutorPage from '../pages/TutorPage/TutorPage';
import LeaderboardPage from '../pages/LeaderboardPage/LeaderboardPage';
import TimeCalculatorPage from '../pages/TimeCalculatorPage/TimeCalculatorPage';
import MessagePage from '../pages/MessagePage/MessagePage';
import AIChatPage from '../pages/AIChatPage/AIChatPage';
import ShopPage from '../pages/ShopPage/ShopPage';
import MomentsPage from '../pages/MomentsPage/MomentsPage';
import SuccessPage from '../pages/SuccessPage/SuccessPage';

const AppRoutes = () => {
  return (
    <Routes>
      {/* 默认路由重定向到时间表 */}
      <Route path="/" element={<Navigate to="/main-schedule" replace />} />
      
      {/* 主要页面路由 */}
      <Route path="/main-schedule" element={<MainSchedulePage />} />
      <Route path="/schedule" element={<SchedulePage />} />
      <Route path="/personal" element={<PersonalPage />} />
      <Route path="/others" element={<OthersPage />} />
      <Route path="/study-method" element={<StudyMethodPage />} />
      <Route path="/tutor" element={<TutorPage />} />
      <Route path="/leaderboard" element={<LeaderboardPage />} />
      <Route path="/calculator" element={<TimeCalculatorPage />} />
      <Route path="/messages" element={<MessagePage />} />
      <Route path="/ai-chat" element={<AIChatPage />} />
      
      {/* 底部导航栏页面路由 */}
      <Route path="/shop" element={<ShopPage />} />
      <Route path="/moments" element={<MomentsPage />} />
      
      {/* 上岸时间表页面 */}
      <Route path="/success" element={<SuccessPage />} />
      
      {/* 404 页面 */}
      <Route 
        path="*" 
        element={
          <div className="not-found-page">
            <div className="container">
              <div className="not-found-content">
                <h1>404</h1>
                <h2>页面未找到</h2>
                <p>抱歉，您访问的页面不存在。</p>
                <button 
                  onClick={() => window.history.back()}
                  className="back-btn"
                >
                  返回上一页
                </button>
              </div>
            </div>
          </div>
        } 
      />
    </Routes>
  );
};

export default AppRoutes; 