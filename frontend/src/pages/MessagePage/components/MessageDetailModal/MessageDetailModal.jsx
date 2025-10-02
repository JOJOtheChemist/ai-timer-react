import React from 'react';
import './MessageDetailModal.css';

const MessageDetailModal = ({ 
  show, 
  messageDetail, 
  activeTab,
  onClose, 
  onFeedbackAction,
  formatTime 
}) => {
  if (!show || !messageDetail) return null;

  return (
    <div 
      className="detail-modal show" 
      onClick={(e) => e.target.className.includes('detail-modal') && onClose()}
    >
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
          <div className="close-modal" onClick={onClose}>×</div>
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
                  <button className="feedback-btn primary" onClick={() => onFeedbackAction('查看时间表')}>
                    查看时间表
                  </button>
                )}
                <button className="feedback-btn secondary" onClick={() => onFeedbackAction('回复导师')}>
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
  );
};

export default MessageDetailModal; 