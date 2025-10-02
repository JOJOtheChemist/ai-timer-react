import React from 'react';
import './MyRelationship.css';

const MyRelationship = ({ 
  relationStats, 
  followedTutors, 
  recentFans, 
  onManageClick, 
  onAvatarClick 
}) => {
  return (
    <div className="relation-section">
      <div className="relation-header">
        <div className="relation-title">我的关系</div>
        <div className="relation-edit" onClick={onManageClick}>管理</div>
      </div>
      
      <div className="relation-stats">
        <div className="relation-item">
          <div className="relation-value">{relationStats.tutor_count}</div>
          <div className="relation-label">关注导师</div>
        </div>
        <div className="relation-item">
          <div className="relation-value">{relationStats.following_count}</div>
          <div className="relation-label">我的学员</div>
        </div>
        <div className="relation-item">
          <div className="relation-value">{relationStats.fan_count}</div>
          <div className="relation-label">粉丝</div>
        </div>
      </div>
      
      <div className="relation-categories">
        <div className="relation-category">
          <div className="category-title">关注的导师</div>
          <div className="relation-list">
            {followedTutors.length > 0 ? followedTutors.map((tutor) => (
              <div 
                key={tutor.tutor_id} 
                className="relation-avatar tutor" 
                onClick={() => onAvatarClick(tutor.name || tutor.tutor_name, '导师')}
              >
                {tutor.avatar || tutor.tutor_avatar ? (
                  <img 
                    src={tutor.avatar || tutor.tutor_avatar} 
                    alt={tutor.name || tutor.tutor_name} 
                    style={{width: '100%', height: '100%', borderRadius: '50%'}} 
                  />
                ) : (tutor.name || tutor.tutor_name || '导').charAt(0)}
                <div className="relation-name">{tutor.name || tutor.tutor_name}</div>
              </div>
            )) : (
              <div style={{color: '#999', fontSize: '12px'}}>暂无关注的导师</div>
            )}
          </div>
        </div>
        
        <div className="relation-category">
          <div className="category-title">最近粉丝</div>
          <div className="relation-list">
            {recentFans.length > 0 ? recentFans.map((fan, index) => (
              <div 
                key={fan.user_id} 
                className="relation-avatar fan" 
                onClick={() => onAvatarClick(fan.username, '粉丝')}
              >
                {fan.avatar ? (
                  <img 
                    src={fan.avatar} 
                    alt={fan.username} 
                    style={{width: '100%', height: '100%', borderRadius: '50%'}} 
                  />
                ) : fan.username.charAt(0)}
                <div className="relation-name">{fan.username}</div>
                {index === 0 && <div className="relation-tag">新</div>}
              </div>
            )) : (
              <div style={{color: '#999', fontSize: '12px'}}>暂无粉丝</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyRelationship; 