import React from 'react';
import './QuickInputBar.css';

const QuickInputBar = ({ quickInput, onQuickInputChange, onQuickAdd }) => {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      onQuickAdd();
    }
  };

  return (
    <div className="quick-input-bar">
      <button className="voice-btn">
        <i className="fa fa-microphone"></i>
      </button>
      <input 
        type="text" 
        placeholder="添加任务备注或对AI说..." 
        value={quickInput}
        onChange={(e) => onQuickInputChange(e.target.value)}
        onKeyPress={handleKeyPress}
        className="quick-input"
      />
      <button 
        onClick={onQuickAdd}
        className="add-btn"
        disabled={!quickInput.trim()}
      >
        <i className="fa fa-plus"></i>
        添加
      </button>
    </div>
  );
};

export default QuickInputBar; 