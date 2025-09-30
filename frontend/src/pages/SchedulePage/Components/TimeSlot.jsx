import React from 'react';

const TimeSlot = ({ 
  slot, 
  selectedMoods, 
  onSetMood, 
  getTaskColor, 
  getStatusIcon, 
  getMoodIcon, 
  getMoodStyle 
}) => {
  return (
    <div 
      className={`time-slot border rounded-lg p-2 transition-colors ${
        slot.isAIRecommended 
          ? 'border-ai/30 bg-ai/5' 
          : slot.status === 'in-progress'
          ? 'border-primary/30 bg-primary/5'
          : slot.status === 'empty'
          ? 'border-dashed border-gray-200 hover:border-primary/30 hover:bg-gray-50'
          : 'border-gray-100 hover:border-primary/30'
      }`}
    >
      <div className="flex justify-between">
        <div className="w-20 text-xs text-gray-500">{slot.time}</div>
        <div className="flex gap-1">
          {/* 心情标记按钮组 */}
          {['happy', 'focused', 'tired'].map(mood => (
            <button
              key={mood}
              className={`w-5 h-5 rounded-full flex items-center justify-center text-xs transition-colors ${
                selectedMoods[slot.id] === mood || slot.mood === mood
                  ? getMoodStyle(mood)
                  : 'bg-gray-100 text-gray-500 hover:' + getMoodStyle(mood)
              }`}
              title={mood === 'happy' ? '愉快' : mood === 'focused' ? '专注' : '疲惫'}
              onClick={() => onSetMood(slot.id, mood)}
            >
              <i className={`fa ${getMoodIcon(mood)}`}></i>
            </button>
          ))}
          {!slot.task && (
            <button className="w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center text-xs text-gray-500 hover:bg-gray-200" title="添加心情">
              <i className="fa fa-plus"></i>
            </button>
          )}
        </div>
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
            <div className="text-xs text-gray-500 mt-0.5">
              <i className={`fa ${getStatusIcon(slot.status)} mr-1`}></i>
              {slot.status === 'completed' ? '已完成' : slot.status === 'in-progress' ? '进行中' : '未开始'}
            </div>
            
            {/* 任务备注 */}
            {slot.note && (
              <div className="mt-1 text-xs bg-gray-50 p-2 rounded border border-gray-100">
                <div className="text-gray-500 mb-0.5">备注：</div>
                <div className="text-gray-700">{slot.note}</div>
              </div>
            )}
            
            {/* AI推荐 */}
            {slot.aiRecommendation && (
              <div className="mt-1 flex items-center text-xs bg-ai/10 p-2 rounded border border-ai/20">
                <i className="fa fa-lightbulb-o text-ai mr-1.5"></i>
                <span className="flex-1">AI推荐：{slot.aiRecommendation}</span>
                <div className="flex gap-1 ml-1">
                  <button className="w-5 h-5 rounded-full bg-white border border-ai/30 flex items-center justify-center text-ai hover:bg-ai hover:text-white transition-colors">
                    <i className="fa fa-check text-xs"></i>
                  </button>
                  <button className="w-5 h-5 rounded-full bg-white border border-gray-300 flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors">
                    <i className="fa fa-times text-xs"></i>
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
            {slot.aiRecommendation && (
              <div className="mt-1 flex items-center text-xs bg-ai/10 p-2 rounded border border-ai/20">
                <i className="fa fa-lightbulb-o text-ai mr-1.5"></i>
                <span className="flex-1">AI推荐：{slot.aiRecommendation}</span>
                <div className="flex gap-1 ml-1">
                  <button className="w-5 h-5 rounded-full bg-white border border-ai/30 flex items-center justify-center text-ai hover:bg-ai hover:text-white transition-colors">
                    <i className="fa fa-check text-xs"></i>
                  </button>
                  <button className="w-5 h-5 rounded-full bg-white border border-gray-300 flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors">
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