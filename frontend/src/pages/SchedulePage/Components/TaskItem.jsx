import React from 'react';

const TaskItem = ({ 
  task, 
  isExpanded, 
  onToggleExpansion, 
  getTaskIcon, 
  getTaskColor 
}) => {
  return (
    <div className={`border-l-2 border-${getTaskColor(task.type)} pl-2 py-1`}>
      <div className="task-item hover:bg-gray-50 transition-colors flex justify-between items-center p-1.5 rounded">
        <div className="flex items-center">
          <i 
            className={`fa ${
              task.subTasks && task.subTasks.length > 0 
                ? (isExpanded ? 'fa-chevron-down' : 'fa-chevron-right') 
                : 'fa-circle-o'
            } text-xs text-gray-400 mr-2 transition-transform duration-200 cursor-pointer`}
            onClick={() => task.subTasks && task.subTasks.length > 0 && onToggleExpansion(task.id)}
          ></i>
          <span className="text-sm">{task.name}</span>
          <span className={`ml-2 bg-${getTaskColor(task.type)}/10 text-${getTaskColor(task.type)} text-xs px-1.5 py-0.5 rounded`}>
            {task.category}
          </span>
          {task.isHighFrequency && (
            <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-frequent text-white text-xs rounded-full">
              <i className="fa fa-bolt"></i>
            </span>
          )}
          {task.isOvercome && (
            <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-warning text-white text-xs rounded-full">
              <i className="fa fa-exclamation"></i>
            </span>
          )}
        </div>
        <div className="text-xs text-gray-500">
          {task.weeklyHours || task.hours}h
        </div>
      </div>
      
      {/* 子任务 */}
      {task.subTasks && task.subTasks.length > 0 && isExpanded && (
        <div className="pl-4 mt-1 space-y-1">
          {task.subTasks.map(subTask => (
            <div key={subTask.id} className="task-item hover:bg-gray-50 transition-colors flex justify-between items-center p-1.5 rounded">
              <div className="flex items-center">
                <i className="fa fa-circle-o text-xs text-gray-400 mr-2"></i>
                <span className="text-sm">{subTask.name}</span>
                {subTask.isHighFrequency && (
                  <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-frequent text-white text-xs rounded-full">
                    <i className="fa fa-bolt"></i>
                  </span>
                )}
                {subTask.isOvercome && (
                  <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-warning text-white text-xs rounded-full">
                    <i className="fa fa-exclamation"></i>
                  </span>
                )}
              </div>
              <div className="text-xs text-gray-500">
                {subTask.hours}h
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TaskItem; 