import React from 'react';
import TaskItem from '../TaskItem/TaskItem';
import './TaskList.css';

const TaskList = ({ tasks, activeFilter, expandedTasks, onToggleTaskExpansion }) => {
  const getTaskColor = (type) => {
    const colorMap = {
      'study': 'study',
      'life': 'life',
      'work': 'work',
      'play': 'play'
    };
    return colorMap[type] || 'gray';
  };

  // 根据筛选条件过滤任务，并且只显示有子任务的项目任务
  const filteredTasks = tasks.filter(task => {
    // 只显示有子任务的任务（项目任务）
    if (!task.subTasks || task.subTasks.length === 0) return false;
    
    // 根据筛选条件过滤
    if (activeFilter === '全部') return true;
    return task.type === activeFilter;
  });

  return (
    <div className="task-list-container">
      {/* 任务列表标题 */}
      <div className="task-list-header">
        <h2 className="font-medium text-sm">高频任务库</h2>
        <button className="text-xs text-primary">
          <i className="fa fa-plus mr-1"></i> 新增
        </button>
      </div>

      {/* 任务标记说明 */}
      <div className="task-legend">
        <div className="legend-item">
          <span className="legend-dot frequent"></span>
          <span>高频</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot warning"></span>
          <span>待克服</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot gray"></span>
          <span>本周时长</span>
        </div>
      </div>

      {/* 任务列表 */}
      <div className="task-list-scroll">
        {filteredTasks.map(task => (
          <TaskItem
            key={task.id}
            task={task}
            isExpanded={expandedTasks[task.id]}
            onToggleExpansion={onToggleTaskExpansion}
            getTaskColor={getTaskColor}
          />
        ))}
      </div>
    </div>
  );
};

export default TaskList; 