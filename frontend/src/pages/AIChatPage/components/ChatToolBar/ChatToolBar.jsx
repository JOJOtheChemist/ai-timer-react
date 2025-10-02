import React from 'react';
import './ChatToolBar.css';

const ChatToolBar = ({ tools, onToolClick }) => {
  return (
    <div className="chat-tool-bar">
      {tools.map((tool, index) => (
        <button 
          key={index}
          className="tool-btn"
          onClick={() => onToolClick(tool)}
        >
          <i>{tool.icon}</i> {tool.text}
        </button>
      ))}
    </div>
  );
};

export default ChatToolBar; 