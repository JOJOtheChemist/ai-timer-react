import React from 'react';
import './AnalysisCards.css';

const AnalysisCards = () => {
  return (
    <div className="analysis-cards">
      {/* 心情-效率分析 */}
      <div className="analysis-card">
        <div className="card-header">
          <h2 className="card-title">心情-效率分析</h2>
          <i className="fa fa-smile-o text-primary"></i>
        </div>
        <div className="card-content">
          <p>• 专注时完成效率提升42%（建议上午9-11点安排核心任务）</p>
          <p>• 数学类任务在心情愉快时正确率高出28%</p>
          <p>• 疲惫期间建议选择轻量任务（如整理笔记）</p>
        </div>
      </div>

      {/* AI 优化建议 */}
      <div className="analysis-card">
        <div className="card-header">
          <h2 className="card-title">AI 优化建议</h2>
          <i className="fa fa-lightbulb-o text-ai"></i>
        </div>
        <div className="card-content">
          <p>• 建议将「高等数学」移至上午（你的专注时段）</p>
          <p>• 英语单词复习频率略低，推荐增加至每日2次</p>
          <p>• 检测到周三学习强度过高，建议均衡分配</p>
        </div>
      </div>
    </div>
  );
};

export default AnalysisCards; 