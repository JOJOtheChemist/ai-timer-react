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
    let baseClass = 'time-slot border rounded-lg p-2 transition-colors';
    if (slot.isAIRecommended) return `${baseClass} border-ai/30 bg-ai/5`;
    if (slot.status === 'in-progress') return `${baseClass} border-primary/30 bg-primary/5`;
    if (slot.status === 'empty') return `${baseClass} border-dashed border-gray-200 hover:border-primary/30 hover:bg-gray-50`;
    return `${baseClass} border-gray-100 hover:border-primary/30`;
  };

  return (
    <div className={getSlotClassName()}>
      <div className="flex justify-between">
        <div className="w-20 text-xs text-gray-500">{slot.time}</div>
        <MoodSelector
          slotId={slot.id}
          selectedMood={selectedMood}
          onMoodSelect={onMoodSelect}
          hasTask={!!slot.task}
        />
      </div>

      
      {slot.task ? (
        <div className="mt-1 flex items-start">
          <div className="w-20"></div>
          <div className="flex-1">
            <div className="flex items-center">
              <span className="text-sm font-medium">{slot.task}</span>
              <span className={`ml-2 bg-${getTaskColor(slot.type)}/10 text-${getTaskColor(slot.type)} text-xs px-1.5 py-0.5 rounded`}>
                {slot.category}
              </span>
              {slot.isHighFrequency && (
                <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-frequent text-white text-xs rounded-full">
                  <i className="fa fa-bolt"></i>
                </span>
              )}
              {slot.isOvercome && (
                <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-warning text-white text-xs rounded-full">
                  <i className="fa fa-exclamation"></i>
                </span>
              )}
              {slot.isAIRecommended && (
                <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-ai text-white text-xs rounded-full">
                  <i className="fa fa-robot"></i>
                </span>
              )}
            </div>
            <div className="text-xs mt-0.5">
              <StatusIcon status={slot.status} />
              <span className="ml-1">
                {slot.status === 'completed' ? '已完成' : 
                 slot.status === 'in-progress' ? '进行中' : 
                 slot.status === 'pending' ? '未开始' : ''}
              </span>
            </div>

            
            {/* 任务备注 */}
            {slot.note && (
              <div className="mt-1 text-xs bg-gray-50 p-2 rounded border border-gray-100">
                <div className="text-gray-500 mb-0.5">备注：</div>
                <div className="text-gray-700">{slot.note}</div>
              </div>
            )}
            
            {/* AI推荐 */}
            {slot.aiTip && (
              <div className="mt-1 flex items-center text-xs bg-ai/10 p-2 rounded border border-ai/20">
                <i className="fa fa-lightbulb-o text-ai mr-1.5"></i>
                <span className="flex-1">AI推荐：{slot.aiTip}</span>
                <div className="flex gap-1 ml-1">
                  <button 
                    onClick={() => onAiRecommendation(slot.id, true)}
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-xs transition-colors ${
                      aiRecommendation === true
                        ? 'bg-ai text-white'
                        : 'bg-white border border-ai/30 text-ai hover:bg-ai hover:text-white'
                    }`}
                  >
                    <i className="fa fa-check"></i>
                  </button>
                  <button 
                    onClick={() => onAiRecommendation(slot.id, false)}
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-xs transition-colors ${
                      aiRecommendation === false
                        ? 'bg-gray-100'
                        : 'bg-white border border-gray-300 text-gray-500 hover:bg-gray-100'
                    }`}
                  >
                    <i className="fa fa-times"></i>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="mt-1 flex items-start">
          <div className="w-20"></div>
          <div className="flex-1">
            <div className="text-sm text-gray-400 mb-1">
              <i className="fa fa-plus-circle mr-1"></i> 点击添加任务
            </div>
            {/* AI推荐任务 */}
            {slot.aiTip && (
              <div className="mt-1 flex items-center text-xs bg-ai/10 p-2 rounded border border-ai/20">
                <i className="fa fa-lightbulb-o text-ai mr-1.5"></i>
                <span className="flex-1">AI推荐：{slot.aiTip}</span>
                <div className="flex gap-1 ml-1">
                  <button 
                    onClick={() => onAiRecommendation(slot.id, true)}
                    className="w-5 h-5 rounded-full bg-white border border-ai/30 flex items-center justify-center text-ai hover:bg-ai hover:text-white transition-colors"
                  >
                    <i className="fa fa-check text-xs"></i>
                  </button>
                  <button 
                    onClick={() => onAiRecommendation(slot.id, false)}
                    className="w-5 h-5 rounded-full bg-white border border-gray-300 flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors"
                  >
                    <i className="fa fa-times text-xs"></i>
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