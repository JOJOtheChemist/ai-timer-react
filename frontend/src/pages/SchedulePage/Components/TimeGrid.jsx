import React from 'react';

const TimeGrid = ({ scheduleData, selectedDate, viewMode, onTaskStatusChange, onCreateTask }) => {
  return (
    <div className="time-grid">
      <div className="time-grid-header">
        <h3>时间网格 ({viewMode === 'day' ? '日视图' : '周视图'})</h3>
      </div>
      
      <div className="grid-container">
        <div className="grid-placeholder">
          <div className="placeholder-icon">📅</div>
          <h4>时间网格组件</h4>
          <p>这里将显示48×7的时间网格</p>
          <p>当前日期: {selectedDate.toLocaleDateString()}</p>
          <p>任务数量: {scheduleData.length}</p>
          
          <div className="sample-tasks">
            <h5>示例任务:</h5>
            {scheduleData.slice(0, 3).map(task => (
              <div key={task.id} className="sample-task">
                <span>{task.title}</span>
                <span className={`status ${task.status}`}>{task.status}</span>
              </div>
            ))}
          </div>
          
          <button 
            onClick={() => onCreateTask && onCreateTask({
              title: "新任务",
              description: "示例任务",
              status: "pending"
            })}
            className="create-task-btn"
          >
            ➕ 创建示例任务
          </button>
        </div>
      </div>
    </div>
  );
};

export default TimeGrid; 