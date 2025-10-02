import React from 'react';
import TimeSlot from '../TimeSlot/TimeSlot';
import './TimeSlotList.css';

const TimeSlotList = ({ 
  timeSlots, 
  selectedMoods, 
  aiRecommendations,
  onMoodSelect, 
  onAiRecommendation 
}) => {
  const getTaskColor = (type) => {
    const colorMap = {
      'study': 'study',
      'life': 'life',
      'work': 'work',
      'play': 'play'
    };
    return colorMap[type] || 'gray';
  };

  return (
    <div className="time-slot-list-container">
      {/* 时间表标题和操作 */}
      <div className="time-slot-list-header">
        <div>
          <h2 className="font-medium text-sm">今日时间表</h2>
          <div className="text-xs text-gray-500">
            实时跟踪 · AI智能推荐
          </div>
        </div>
        <div className="header-actions">
          <button className="action-btn reset">
            <i className="fa fa-refresh mr-1"></i> 重置
          </button>
          <button className="action-btn ai">
            <i className="fa fa-magic mr-1"></i> AI规划
          </button>
        </div>
      </div>

      {/* 时间表内容 */}
      <div className="time-slot-list-scroll">
        {timeSlots.map(slot => (
          <TimeSlot
            key={slot.id}
            slot={slot}
            selectedMood={selectedMoods[slot.id]}
            aiRecommendation={aiRecommendations[slot.id]}
            onMoodSelect={onMoodSelect}
            onAiRecommendation={onAiRecommendation}
            getTaskColor={getTaskColor}
          />
        ))}
      </div>
    </div>
  );
};

export default TimeSlotList; 