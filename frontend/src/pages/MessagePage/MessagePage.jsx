import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './MessagePage.css';
import messageService from '../../services/messageService';

// 导入子组件
import {
  MessageHeader,
  MessageTabs,
  MessageList,
  MessageFooter,
  MessageDetailModal
} from './components';

const MessagePage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('tutor');
  const [showDetailModal, setShowDetailModal] = useState(false);
  const USER_ID = 101; // TODO: 从认证系统获取

  // 数据状态
  const [tutorMessages, setTutorMessages] = useState([]);
  const [privateMessages, setPrivateMessages] = useState([]);
  const [systemMessages, setSystemMessages] = useState([]);
  const [unreadStats, setUnreadStats] = useState({ tutor_count: 0, private_count: 0, system_count: 0 });
  const [loading, setLoading] = useState(true);
  const [messageDetail, setMessageDetail] = useState(null);

  // 加载消息列表
  const loadMessages = async (type) => {
    try {
      setLoading(true);
      const response = await messageService.getMessageList({
        message_type: type,
        user_id: USER_ID,
        page: 1,
        page_size: 20
      });

      // 根据类型设置不同的状态
      if (type === 'tutor') {
        setTutorMessages(response.messages || []);
      } else if (type === 'private') {
        setPrivateMessages(response.messages || []);
      } else if (type === 'system') {
        setSystemMessages(response.messages || []);
      }
    } catch (error) {
      console.error(`加载${type}消息失败:`, error);
    } finally {
      setLoading(false);
    }
  };

  // 加载未读统计
  const loadUnreadStats = async () => {
    try {
      const stats = await messageService.getUnreadStats(USER_ID);
      setUnreadStats(stats);
    } catch (error) {
      console.error('加载未读统计失败:', error);
    }
  };

  // 初始化：加载当前tab的消息和未读统计
  useEffect(() => {
    loadMessages(activeTab);
    loadUnreadStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 切换tab时重新加载
  useEffect(() => {
    loadMessages(activeTab);
  }, [activeTab]);

  // 事件处理函数
  const handleTabClick = (tabType) => {
    setActiveTab(tabType);
  };

  const handleMessageClick = async (message) => {
    try {
      // 获取消息详情
      const detail = await messageService.getMessageDetail(message.id, USER_ID);
      setMessageDetail(detail);
      setShowDetailModal(true);

      // 如果消息未读，标记为已读
      if (message.is_unread) {
        await messageService.markAsRead(message.id, USER_ID);
        // 重新加载消息列表和统计
        loadMessages(activeTab);
        loadUnreadStats();
      }
    } catch (error) {
      console.error('获取消息详情失败:', error);
    }
  };

  const closeModal = () => {
    setShowDetailModal(false);
    setMessageDetail(null);
  };

  const handleFeedbackAction = (action) => {
    setShowDetailModal(false);
    
    if (action === '查看时间表') {
      navigate('/schedule');
    } else if (action === '回复导师') {
      alert('回复功能开发中');
    } else if (action === '查看私信') {
      setActiveTab('private');
    }
  };

  const handleSettingClick = () => {
    alert('打开消息设置页面（可设置提醒方式、消息清理等）');
  };

  const handleBack = () => {
    navigate(-1);
  };

  // 格式化时间
  const formatTime = (timeStr) => {
    if (!timeStr) return '';
    const date = new Date(timeStr);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) {
      return `${minutes}分钟前`;
    } else if (hours < 24) {
      return `${hours}小时前`;
    } else if (days < 7) {
      return `${days}天前`;
    } else {
      return date.toLocaleDateString();
    }
  };

  // 加载状态
  if (loading && tutorMessages.length === 0 && privateMessages.length === 0 && systemMessages.length === 0) {
    return (
      <div className="message-page">
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
          加载中...
        </div>
        <BottomNavBar />
      </div>
    );
  }

  return (
    <div className="message-page">
      {/* 顶部导航栏 */}
      <MessageHeader 
        onBack={handleBack}
        onSettingClick={handleSettingClick}
      />

      {/* 标签页切换 */}
      <MessageTabs 
        activeTab={activeTab}
        onTabChange={handleTabClick}
        unreadStats={unreadStats}
      />

      {/* 消息列表 */}
      <MessageList 
        activeTab={activeTab}
        tutorMessages={tutorMessages}
        privateMessages={privateMessages}
        systemMessages={systemMessages}
        onMessageClick={handleMessageClick}
        formatTime={formatTime}
      />

      {/* 消息详情弹窗 */}
      <MessageDetailModal 
        show={showDetailModal}
        messageDetail={messageDetail}
        activeTab={activeTab}
        onClose={closeModal}
        onFeedbackAction={handleFeedbackAction}
        formatTime={formatTime}
      />

      {/* 底部提示 */}
      <MessageFooter />

      <BottomNavBar />
    </div>
  );
};

export default MessagePage; 