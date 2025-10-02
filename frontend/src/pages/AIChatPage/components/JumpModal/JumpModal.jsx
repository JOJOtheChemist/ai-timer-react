import React from 'react';
import './JumpModal.css';

const JumpModal = ({ isOpen, modalConfig, onConfirm, onCancel }) => {
  if (!isOpen) return null;

  const { icon, title, desc } = modalConfig;

  return (
    <div className="jump-modal show" onClick={onCancel}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-icon">{icon}</div>
        <div className="modal-title">{title}</div>
        <div className="modal-desc">{desc}</div>
        <div className="modal-actions">
          <button className="modal-btn cancel" onClick={onCancel}>
            取消
          </button>
          <button className="modal-btn confirm" onClick={onConfirm}>
            确定
          </button>
        </div>
      </div>
    </div>
  );
};

export default JumpModal; 