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
    <div className="bg-white rounded-xl shadow-sm p-3 h-full">
      {/* 时间表标题和操作 */}
      <div className="flex justify-between items-center mb-3">
        <h2 className="font-medium text-sm">今日时间表</h2>
        <div className="flex gap-2">
          <button className="text-xs text-gray-500 hover:text-primary">
            <i className="fa fa-refresh mr-1"></i> 重置
          </button>
          <button className="text-xs bg-ai/10 text-ai">
            <i className="fa fa-magic mr-1"></i> AI规划
          </button>
        </div>
      </div>

      {/* 时间表内容 */}
      <div className="space-y-2 max-h-[400px] overflow-y-auto scrollbar-thin pr-1">
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