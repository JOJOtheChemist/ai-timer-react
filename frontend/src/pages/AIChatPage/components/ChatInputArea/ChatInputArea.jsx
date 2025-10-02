import React from 'react';
import './ChatInputArea.css';

const ChatInputArea = ({ inputValue, onInputChange, onSend, onKeyDown }) => {
  return (
    <div className="chat-input-area">
      <div className="input-container">
        <div className="input-tools">
          <i>🎤</i>
          <i>📷</i>
          <i>📎</i>
        </div>
        <input 
          type="text" 
          className="input-box" 
          placeholder="和AI聊聊你的时间表或需求..."
          value={inputValue}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={onKeyDown}
        />
        <button className="send-btn" onClick={onSend}>→</button>
      </div>
    </div>
  );
};

export default ChatInputArea; 