import React, { useState } from 'react';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './MessagePage.css';

const MessagePage = () => {
  const [activeTab, setActiveTab] = useState('tutor');
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedMessage, setSelectedMessage] = useState(null);

  const handleTabClick = (tabType) => {
    setActiveTab(tabType);
  };

  const handleTutorMessageClick = (msgId) => {
    setSelectedMessage(msgId);
    setShowDetailModal(true);
  };

  const closeModal = () => {
    setShowDetailModal(false);
    setSelectedMessage(null);
  };

  const handleFeedbackAction = (action) => {
    setShowDetailModal(false);
    
    if (action === '查看时间表') {
      alert('跳转至7月15日英语学习时间表详情页');
    } else if (action === '回复导师') {
      alert('跳转至与王英语老师的私信界面');
    } else if (action === '查看私信') {
      setActiveTab('private');
    }
  };

  const handleSettingClick = () => {
    alert('打开消息设置页面（可设置提醒方式、消息清理等）');
  };

  return (
    <div className="message-page">
      {/* 顶部导航栏 */}
      <div className="nav-top">
        <div className="back-btn">←</div>
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
          <span className="badge">2</span>
        </button>
        <button 
          className={`tab-btn ${activeTab === 'private' ? 'active' : ''}`}
          onClick={() => handleTabClick('private')}
        >
          私信
          <span className="badge">1</span>
        </button>
        <button 
          className={`tab-btn ${activeTab === 'system' ? 'active' : ''}`}
          onClick={() => handleTabClick('system')}
        >
          系统通知
        </button>
      </div>

      {/* 导师反馈页 */}
      <div className={`msg-container ${activeTab === 'tutor' ? 'active' : ''}`}>
        <div className="msg-list">
          {/* 未读消息：王英语老师 */}
          <div className="msg-item" onClick={() => handleTutorMessageClick('1')}>
            <div className="msg-avatar tutor">👩‍🏫</div>
            <div className="msg-content">
              <div className="msg-header">
                <div className="msg-name">王英语老师 <span className="msg-tag">认证导师</span></div>
                <div className="msg-time">09:42</div>
              </div>
              <div className="msg-text highlight">
                <span className="msg-badge"></span>
                你的英语时间表有3处可优化，重点调整阅读时长...
              </div>
            </div>
          </div>

          {/* 未读消息：李会计学姐 */}
          <div className="msg-item" onClick={() => handleTutorMessageClick('2')}>
            <div className="msg-avatar tutor">👩‍💼</div>
            <div className="msg-content">
              <div className="msg-header">
                <div className="msg-name">李会计学姐 <span className="msg-tag">普通导师</span></div>
                <div className="msg-time">昨天 18:30</div>
              </div>
              <div className="msg-text highlight">
                <span className="msg-badge"></span>
                CPA税法高频考点整理好了，结合你的时间表...
              </div>
            </div>
          </div>

          {/* 已读消息：张编程导师 */}
          <div className="msg-item" onClick={() => handleTutorMessageClick('3')}>
            <div className="msg-avatar tutor">👩‍💻</div>
            <div className="msg-content">
              <div className="msg-header">
                <div className="msg-name">张编程导师 <span className="msg-tag">认证导师</span></div>
                <div className="msg-time">3天前</div>
              </div>
              <div className="msg-text">
                你的Python学习计划很合理，坚持每日代码练习即可~
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 私信页 */}
      <div className={`msg-container ${activeTab === 'private' ? 'active' : ''}`}>
        <div className="search-bar">
          <i>🔍</i>
          <input type="text" placeholder="搜索联系人" />
        </div>
        <div className="msg-list">
          {/* 未读消息：考研的小琳 */}
          <div className="msg-item">
            <div className="msg-avatar">👩‍🎓</div>
            <div className="msg-content">
              <div className="msg-header">
                <div className="msg-name">考研的小琳</div>
                <div className="msg-time">10:15</div>
              </div>
              <div className="msg-text highlight">
                <span className="msg-badge"></span>
                你用的艾宾浩斯复习法真的好用！求打卡模板~
              </div>
            </div>
          </div>

          {/* 已读消息：学Python的阿美 */}
          <div className="msg-item">
            <div className="msg-avatar">👩‍💻</div>
            <div className="msg-content">
              <div className="msg-header">
                <div className="msg-name">学Python的阿美</div>
                <div className="msg-time">昨天 20:12</div>
              </div>
              <div className="msg-text">
                分享给你一个Python刷题网站，亲测有效！
              </div>
            </div>
          </div>

          {/* 已读消息：考公的小楠 */}
          <div className="msg-item">
            <div className="msg-avatar">📝</div>
            <div className="msg-content">
              <div className="msg-header">
                <div className="msg-name">考公的小楠</div>
                <div className="msg-time">4天前</div>
              </div>
              <div className="msg-text">
                常识模块的复习时间表整理好啦，发你看看~
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 系统通知页 */}
      <div className={`msg-container ${activeTab === 'system' ? 'active' : ''}`}>
        <div className="msg-list">
          {/* 徽章通知 */}
          <div className="msg-item">
            <div className="msg-avatar system">🏆</div>
            <div className="msg-content">
              <div className="msg-header">
                <div className="msg-name">徽章通知</div>
                <div className="msg-time">今天 08:00</div>
              </div>
              <div className="msg-text">
                你连续7天打卡复习法，获得「坚持之星」徽章！
              </div>
            </div>
          </div>

          {/* 钻石通知 */}
          <div className="msg-item">
            <div className="msg-avatar system">💎</div>
            <div className="msg-content">
              <div className="msg-header">
                <div className="msg-name">钻石通知</div>
                <div className="msg-time">昨天 14:30</div>
              </div>
              <div className="msg-text">
                分享上岸案例获得10钻石奖励，已到账~
              </div>
            </div>
          </div>

          {/* 活动通知 */}
          <div className="msg-item">
            <div className="msg-avatar system">📢</div>
            <div className="msg-content">
              <div className="msg-header">
                <div className="msg-name">活动通知</div>
                <div className="msg-time">3天前</div>
              </div>
              <div className="msg-text">
                「上传时间表赢真皮包」活动剩最后5天，快去参与！
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 导师反馈详情弹窗 */}
      {showDetailModal && (
        <div className="detail-modal show" onClick={(e) => e.target.className.includes('detail-modal') && closeModal()}>
          <div className="modal-content">
            <div className="modal-header">
              <div className="modal-avatar">👩‍🏫</div>
              <div className="modal-info">
                <div className="modal-name">王英语老师</div>
                <div className="modal-meta">认证导师 · 考研英语 | 09:42</div>
              </div>
              <div className="close-modal" onClick={closeModal}>×</div>
            </div>
            <div className="modal-body">
              <div className="feedback-item">
                <div className="feedback-header">
                  <div className="feedback-title">针对你7月15日的英语学习时间表</div>
                  <div className="feedback-time">今天 09:42</div>
                </div>
                <div className="feedback-content">
                  你好！查看了你的英语时间表，发现几个可以优化的点：<br />
                  1. <span className="feedback-highlight">阅读时长过长</span>：每天2.5h远超建议的1.5h，效率会下降，建议拆分1h精读+0.5h泛读；<br />
                  2. <span className="feedback-highlight">复习缺失</span>：近3天未安排单词复习，推荐用艾宾浩斯法嵌入碎片时间；<br />
                  3. <span className="feedback-highlight">时段适配</span>：你早上记忆力最佳，可将单词复习调整至7:00-7:30。
                </div>
                <div className="feedback-actions">
                  <button className="feedback-btn primary" onClick={() => handleFeedbackAction('查看时间表')}>
                    查看时间表
                  </button>
                  <button className="feedback-btn secondary" onClick={() => handleFeedbackAction('回复导师')}>
                    回复导师
                  </button>
                </div>
              </div>
              <div className="feedback-item">
                <div className="feedback-header">
                  <div className="feedback-title">针对你7月14日的英语学习时间表</div>
                  <div className="feedback-time">昨天 16:20</div>
                </div>
                <div className="feedback-content">
                  作文模板已发送至你的私信，记得结合每日练习套用，重点关注三段式结构~
                </div>
                <div className="feedback-actions">
                  <button className="feedback-btn secondary" onClick={() => handleFeedbackAction('查看私信')}>
                    查看私信
                  </button>
                </div>
              </div>
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