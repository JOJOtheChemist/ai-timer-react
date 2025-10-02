import React from 'react';
import './CheckinModal.css';

const CheckinModal = ({
  show,
  method,
  checkinType,
  checkinProgress,
  checkinNote,
  onClose,
  onTypeChange,
  onProgressChange,
  onNoteChange,
  onComplete,
  getCheckinItems
}) => {
  if (!show || !method) return null;

  return (
    <div className="checkin-modal show" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="icon">
            {method.type === 'tutor' ? '👩‍🏫' : '📚'}
          </div>
          <div className="title">{method.name} · 打卡</div>
        </div>
        
        <div className="checkin-type">
          {['正字打卡', '计数打卡'].map(type => (
            <div
              key={type}
              className={`checkin-option ${checkinType === type ? 'active' : ''}`}
              onClick={() => onTypeChange(type)}
            >
              {type}
            </div>
          ))}
        </div>
        
        <div className="checkin-content">
          <div className="checkin-count">
            {getCheckinItems().map((item, index) => (
              <div
                key={index}
                className={`checkin-item ${index < checkinProgress ? 'active' : ''}`}
                onClick={() => onProgressChange(index + 1)}
              >
                {item}
              </div>
            ))}
          </div>
          <textarea
            className="checkin-note"
            placeholder="记录今日复习心得（可选）"
            value={checkinNote}
            onChange={(e) => onNoteChange(e.target.value)}
          />
        </div>
        
        <div className="modal-actions">
          <button className="modal-btn cancel" onClick={onClose}>
            取消
          </button>
          <button className="modal-btn confirm" onClick={onComplete}>
            完成打卡
          </button>
        </div>
      </div>
    </div>
  );
};

export default CheckinModal; 