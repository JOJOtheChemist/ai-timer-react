import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './MessagePage.css';
import messageService from '../../services/messageService';

const MessagePage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('tutor');
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState(null);
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
  }, []);

  // 切换tab时重新加载
  useEffect(() => {
    loadMessages(activeTab);
  }, [activeTab]);

  const handleTabClick = (tabType) => {
    setActiveTab(tabType);
  };

  const handleMessageClick = async (message) => {
    try {
      // 获取消息详情
      const detail = await messageService.getMessageDetail(message.id, USER_ID);
      setMessageDetail(detail);
      setSelectedMessage(message);
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
    setSelectedMessage(null);
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

  // 渲染消息项
  const renderMessageItem = (message, type) => {
    const isUnread = message.is_unread === 1;
    
    return (
      <div 
        key={message.id} 
        className="msg-item" 
        onClick={() => handleMessageClick(message)}
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
      <div className="nav-top">
        <div className="back-btn" onClick={() => navigate(-1)}>←</div>
        <div className="title">消息中心</div>
        <div className="setting-btn" onClick={handleSettingClick}>⚙️</div>
      </div>

      {/* 标签页切换 */}
      <div className="tab-container">
        <button 
          className={`tab-btn ${activeTab === 'tutor' ? 'active' : ''}`}
          onClick={() => handleTabClick('tutor')}
        >
          导师反馈
          {unreadStats.tutor_count > 0 && <span className="badge">{unreadStats.tutor_count}</span>}
        </button>
        <button 
          className={`tab-btn ${activeTab === 'private' ? 'active' : ''}`}
          onClick={() => handleTabClick('private')}
        >
          私信
          {unreadStats.private_count > 0 && <span className="badge">{unreadStats.private_count}</span>}
        </button>
        <button 
          className={`tab-btn ${activeTab === 'system' ? 'active' : ''}`}
          onClick={() => handleTabClick('system')}
        >
          系统通知
          {unreadStats.system_count > 0 && <span className="badge">{unreadStats.system_count}</span>}
        </button>
      </div>

      {/* 导师反馈页 */}
      <div className={`msg-container ${activeTab === 'tutor' ? 'active' : ''}`}>
        <div className="msg-list">
          {tutorMessages.length > 0 ? (
            tutorMessages.map(msg => renderMessageItem(msg, 'tutor'))
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              暂无导师反馈
            </div>
          )}
        </div>
      </div>

      {/* 私信页 */}
      <div className={`msg-container ${activeTab === 'private' ? 'active' : ''}`}>
        <div className="search-bar">
          <i>🔍</i>
          <input type="text" placeholder="搜索联系人" />
        </div>
        <div className="msg-list">
          {privateMessages.length > 0 ? (
            privateMessages.map(msg => renderMessageItem(msg, 'private'))
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              暂无私信
            </div>
          )}
        </div>
      </div>

      {/* 系统通知页 */}
      <div className={`msg-container ${activeTab === 'system' ? 'active' : ''}`}>
        <div className="msg-list">
          {systemMessages.length > 0 ? (
            systemMessages.map(msg => renderMessageItem(msg, 'system'))
          ) : (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              暂无系统通知
            </div>
          )}
        </div>
      </div>

      {/* 消息详情弹窗 */}
      {showDetailModal && messageDetail && (
        <div className="detail-modal show" onClick={(e) => e.target.className.includes('detail-modal') && closeModal()}>
          <div className="modal-content">
            <div className="modal-header">
              <div className="modal-avatar">
                {messageDetail.sender_avatar || '👤'}
              </div>
              <div className="modal-info">
                <div className="modal-name">{messageDetail.sender_name || '系统'}</div>
                <div className="modal-meta">
                  {activeTab === 'tutor' && messageDetail.tutor_certification && (
                    <span>{messageDetail.tutor_certification === 'verified' ? '认证导师' : '普通导师'} · </span>
                  )}
                  {messageDetail.tutor_major && <span>{messageDetail.tutor_major} | </span>}
                  {formatTime(messageDetail.create_time)}
                </div>
              </div>
              <div className="close-modal" onClick={closeModal}>×</div>
            </div>
            <div className="modal-body">
              <div className="feedback-item">
                <div className="feedback-header">
                  {messageDetail.title && (
                    <div className="feedback-title">{messageDetail.title}</div>
                  )}
                  <div className="feedback-time">{formatTime(messageDetail.create_time)}</div>
                </div>
                <div className="feedback-content">
                  {messageDetail.content.split('\n').map((line, idx) => (
                    <React.Fragment key={idx}>
                      {line}
                      {idx < messageDetail.content.split('\n').length - 1 && <br />}
                    </React.Fragment>
                  ))}
                </div>
                {activeTab === 'tutor' && (
                  <div className="feedback-actions">
                    {messageDetail.related_type === 'schedule' && (
                      <button className="feedback-btn primary" onClick={() => handleFeedbackAction('查看时间表')}>
                        查看时间表
                      </button>
                    )}
                    <button className="feedback-btn secondary" onClick={() => handleFeedbackAction('回复导师')}>
                      回复导师
                    </button>
                  </div>
                )}
              </div>

              {/* 显示上下文消息（历史对话） */}
              {messageDetail.context_messages && messageDetail.context_messages.length > 0 && (
                <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #eee' }}>
                  <h4 style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>历史对话</h4>
                  {messageDetail.context_messages.map((ctx, idx) => (
                    <div key={idx} className="feedback-item" style={{ marginBottom: '15px' }}>
                      <div className="feedback-header">
                        {ctx.title && <div className="feedback-title">{ctx.title}</div>}
                        <div className="feedback-time">{formatTime(ctx.create_time)}</div>
                      </div>
                      <div className="feedback-content" style={{ fontSize: '13px' }}>
                        {ctx.content}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 底部提示 */}
      <div className="bottom-tip">
        导师反馈优先推送 | 未读消息保留7天，可在设置中调整提醒方式
      </div>

      <BottomNavBar />
    </div>
  );
};

export default MessagePage; 