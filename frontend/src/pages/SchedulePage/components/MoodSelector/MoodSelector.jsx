import React from 'react';

const MoodSelector = ({ slotId, selectedMood, onMoodSelect, hasTask }) => {
  const moods = ['happy', 'focused', 'tired'];

  const getMoodIcon = (mood) => {
    const iconMap = {
      'happy': 'fa-smile-o',
      'focused': 'fa-eye',
      'tired': 'fa-tired'
    };
    return iconMap[mood] || 'fa-plus';
  };

  const getMoodTitle = (mood) => {
    const titleMap = {
      'happy': '愉快',
      'focused': '专注',
      'tired': '疲惫'
    };
    return titleMap[mood] || '';
  };

  const getMoodStyle = (mood, isSelected) => {
    const baseStyle = "w-5 h-5 rounded-full flex items-center justify-center text-xs transition-colors";
    if (isSelected) {
      const selectedStyles = {
        'happy': 'bg-yellow-100 text-yellow-500',
        'focused': 'bg-blue-100 text-blue-500',
        'tired': 'bg-red-100 text-red-500'
      };
      return `${baseStyle} ${selectedStyles[mood] || 'bg-gray-100 text-gray-500'}`;
    }
    return `${baseStyle} bg-gray-100 text-gray-500 hover:bg-${mood === 'happy' ? 'yellow' : mood === 'focused' ? 'blue' : 'red'}-100`;
  };

  return (
    <div className="flex gap-1">
      {/* 心情标记按钮组 */}
      {moods.map(mood => (
        <button
          key={mood}
          onClick={() => onMoodSelect(slotId, mood)}
          className={getMoodStyle(mood, selectedMood === mood)}
          title={getMoodTitle(mood)}
        >
          <i className={`fa ${getMoodIcon(mood)}`}></i>
        </button>
      ))}
      {!hasTask && (
        <button 
          className="w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center text-xs text-gray-500 hover:bg-gray-200" 
          title="添加心情"
        >
          <i className="fa fa-plus"></i>
        </button>
      )}
    </div>
  );
};

export default MoodSelector; 