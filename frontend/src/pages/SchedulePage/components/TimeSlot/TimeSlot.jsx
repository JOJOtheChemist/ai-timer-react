import React from 'react';
import MoodSelector from '../MoodSelector/MoodSelector';
import StatusIcon from '../StatusIcon/StatusIcon';
import './TimeSlot.css';

const TimeSlot = ({ 
  slot, 
  selectedMood, 
  aiRecommendation,
  onMoodSelect, 
  onAiRecommendation,
  getTaskColor 
}) => {
  const getSlotClassName = () => {
    if (slot.isAIRecommended) return 'time-slot ai-recommended';
    if (slot.status === 'in-progress') return 'time-slot in-progress';
    if (slot.status === 'empty') return 'time-slot empty';
    return 'time-slot';
  };

  return (
    <div className={getSlotClassName()}>
      <div className="slot-header">
        <div className="slot-time">{slot.time}</div>
        <MoodSelector
          slotId={slot.id}
          selectedMood={selectedMood}
          onMoodSelect={onMoodSelect}
        />
      </div>
      
      {slot.task ? (
        <div className="slot-content">
          <div className="slot-content-offset"></div>
          <div className="slot-task-details">
            <div className="task-info-row">
              <span className="task-name">{slot.task}</span>
              <span className={`task-category ${getTaskColor(slot.type)}`}>
                {slot.category}
              </span>
              {slot.isHighFrequency && (
                <span className="task-badge frequent">
                  <i className="fa fa-bolt"></i>
                </span>
              )}
              {slot.isOvercome && (
                <span className="task-badge warning">
                  <i className="fa fa-exclamation"></i>
                </span>
              )}
              {slot.isAIRecommended && (
                <span className="task-badge ai">
                  <i className="fa fa-robot"></i>
                </span>
              )}
            </div>
            <div className="task-status">
              <StatusIcon status={slot.status} />
              <span className="ml-1">
                {slot.status === 'completed' ? '已完成' : 
                 slot.status === 'in-progress' ? '进行中' : 
                 slot.status === 'pending' ? '未开始' : ''}
              </span>
            </div>
            
            {/* 任务备注 */}
            {slot.note && (
              <div className="task-note">
                <div className="note-label">备注：</div>
                <div className="note-content">{slot.note}</div>
              </div>
            )}
            
            {/* AI推荐 */}
            {slot.aiTip && (
              <div className="ai-tip">
                <i className="fa fa-lightbulb-o text-ai mr-1.5"></i>
                <span className="flex-1">AI推荐：{slot.aiTip}</span>
                <div className="ai-actions">
                  <button 
                    onClick={() => onAiRecommendation(slot.id, true)}
                    className={`ai-action-btn ${aiRecommendation === true ? 'active' : ''}`}
                  >
                    <i className="fa fa-check"></i>
                  </button>
                  <button 
                    onClick={() => onAiRecommendation(slot.id, false)}
                    className={`ai-action-btn ${aiRecommendation === false ? 'active' : ''}`}
                  >
                    <i className="fa fa-times"></i>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="slot-content">
          <div className="slot-content-offset"></div>
          <div className="slot-task-details">
            <div className="empty-slot">
              <i className="fa fa-plus-circle mr-1"></i> 点击添加任务
            </div>
            {/* AI推荐任务 */}
            {slot.aiTip && (
              <div className="ai-tip">
                <i className="fa fa-lightbulb-o text-ai mr-1.5"></i>
                <span className="flex-1">AI推荐：{slot.aiTip}</span>
                <div className="ai-actions">
                  <button 
                    onClick={() => onAiRecommendation(slot.id, true)}
                    className="ai-action-btn"
                  >
                    <i className="fa fa-check"></i>
                  </button>
                  <button 
                    onClick={() => onAiRecommendation(slot.id, false)}
                    className="ai-action-btn"
                  >
                    <i className="fa fa-times"></i>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TimeSlot; 