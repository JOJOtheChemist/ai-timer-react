import React from 'react';
import RecommendCard from '../RecommendCard/RecommendCard';
import './ChatMessageItem.css';

const ChatMessageItem = ({ message, onRecommendClick }) => {
  const { type, avatar, content, time, isAnalysis, analysisData, hasRecommendation, recommendation } = message;

  return (
    <div className={`msg-wrapper ${type}`}>
      <div className="msg-avatar">{avatar}</div>
      <div className="msg-bubble">
        {isAnalysis ? (
          // 分析类消息
          <div>
            <div>你的时间表关键问题：</div>
            <div style={{ margin: '8px 0' }}>
              {analysisData.tags.map((tag, index) => (
                <span key={index} className="analysis-tag">{tag}</span>
              ))}
            </div>
            <div>{analysisData.analysis}</div>

            {/* 推荐学习方法 */}
            <div className="recommend-section">
              <div className="recommend-title">
                <i>🔄</i> 为你推荐学习方法
              </div>
              <div className="recommend-list">
                <RecommendCard
                  recommendData={analysisData.recommendations[0]}
                  onClick={onRecommendClick}
                />
              </div>
            </div>

            {/* 推荐相似案例 */}
            <div className="recommend-section">
              <div className="recommend-title">
                <i>📅</i> 相似上岸案例参考
              </div>
              <div className="recommend-list">
                <RecommendCard
                  recommendData={analysisData.recommendations[1]}
                  onClick={onRecommendClick}
                />
              </div>
            </div>

            {/* 推荐匹配导师 */}
            <div className="recommend-section">
              <div className="recommend-title">
                <i>👩‍🏫</i> 匹配擅长领域导师
              </div>
              <div className="recommend-list">
                <RecommendCard
                  recommendData={analysisData.recommendations[2]}
                  onClick={onRecommendClick}
                />
              </div>
            </div>
          </div>
        ) : (
          // 普通文本消息
          <div>
            {content.split('\n').map((line, index) => (
              <div key={index}>{line}</div>
            ))}
            
            {/* 附带推荐 */}
            {hasRecommendation && (
              <div className="recommend-section" style={{ marginTop: '8px' }}>
                <div className="recommend-list">
                  <RecommendCard
                    recommendData={recommendation}
                    onClick={onRecommendClick}
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
      <div className="msg-time">{time}</div>
    </div>
  );
};

export default ChatMessageItem; 