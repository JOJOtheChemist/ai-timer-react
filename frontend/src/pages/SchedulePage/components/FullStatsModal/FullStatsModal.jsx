import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import './FullStatsModal.css';

const FullStatsModal = ({ 
  showFullStats, 
  onClose, 
  doughnutChartData, 
  doughnutOptions 
}) => {
  if (!showFullStats) return null;

  return (
    <div className="full-stats-modal" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">完整统计分析</h2>
          <button onClick={onClose} className="modal-close-btn">
            <i className="fa fa-times"></i>
          </button>
        </div>
        
        <div className="modal-body">
          {/* 任务类别分布 */}
          <div className="stats-section">
            <h3 className="section-title">任务类别时长分布</h3>
            <div className="chart-container">
              <Doughnut data={doughnutChartData} options={doughnutOptions} />
            </div>
          </div>
          
          {/* 高频任务 */}
          <div className="stats-section">
            <h3 className="section-title">高频任务 TOP3</h3>
            <div className="task-list">
              <div className="task-row">
                <span className="task-rank">1</span>
                <span className="task-name">英语单词记忆</span>
                <span className="task-time">12.5h</span>
              </div>
              <div className="task-row">
                <span className="task-rank">2</span>
                <span className="task-name">高等数学练习</span>
                <span className="task-time">8.0h</span>
              </div>
              <div className="task-row">
                <span className="task-rank">3</span>
                <span className="task-name">专业课复习</span>
                <span className="task-time">6.5h</span>
              </div>
            </div>
          </div>
          
          {/* 待克服任务 */}
          <div className="stats-section">
            <h3 className="section-title">待克服任务</h3>
            <div className="task-list">
              <div className="task-row warning">
                <i className="fa fa-exclamation-triangle"></i>
                <span className="task-name">专业课真题练习</span>
                <span className="task-status">完成率 40%</span>
              </div>
              <div className="task-row warning">
                <i className="fa fa-exclamation-triangle"></i>
                <span className="task-name">英语阅读理解</span>
                <span className="task-status">完成率 55%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FullStatsModal; 