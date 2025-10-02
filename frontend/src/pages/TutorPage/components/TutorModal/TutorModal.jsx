import React from 'react';
import './TutorModal.css';

const TutorModal = ({ show, tutor, onClose, onServicePurchase, onMessage, onFollow }) => {
  if (!show || !tutor) return null;

  return (
    <div className="tutor-modal show" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="close-modal" onClick={onClose}>×</div>
        
        <div className="modal-header">
          <div className="modal-avatar">{tutor.avatar}</div>
          <div className="modal-header-info">
            <div className="modal-name">{tutor.name}</div>
            <div className={`tutor-tag ${tutor.type}`}>
              {tutor.type === 'certified' ? '认证导师' : '普通导师'}
            </div>
            <div className="modal-domain">{tutor.domain}</div>
            <div className="modal-metrics">
              <div className={`modal-metric ${tutor.metrics.rating >= 97 ? 'highlight' : ''}`}>
                ⭐ {tutor.metrics.rating}%好评
              </div>
              <div className="modal-metric">
                👥 {tutor.metrics.students}人指导
              </div>
              <div className={`modal-metric ${tutor.metrics.successRate >= 85 ? 'highlight' : ''}`}>
                🎯 {tutor.metrics.successRate}%上岸
              </div>
            </div>
          </div>
        </div>

        {/* 导师Profile */}
        {tutor.profile && (
          <div className="modal-section">
            <div className="section-subtitle">导师Profile</div>
            <div className="profile-content">
              <p>✅ 教育背景：{tutor.profile.education}</p>
              <p>✅ 上岸经历：{tutor.profile.experience}</p>
              <p>✅ 工作经历：{tutor.profile.work}</p>
              <p>✅ 指导理念：{tutor.profile.philosophy}</p>
            </div>
          </div>
        )}

        {/* 服务列表 */}
        {tutor.serviceDetails && (
          <div className="modal-section">
            <div className="section-subtitle">提供服务</div>
            <div className="service-list">
              {tutor.serviceDetails.map((service, index) => (
                <div key={index} className="service-card">
                  <div className="service-info">
                    <div className="service-name">{service.name}</div>
                    <div className="service-desc">{service.desc}</div>
                  </div>
                  <div className="service-action">
                    <div className="service-price">
                      {service.price}钻石{service.unit || ''}
                    </div>
                    <button 
                      className="buy-btn"
                      onClick={() => onServicePurchase(service)}
                    >
                      购买
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 数据面板 */}
        {tutor.dataPanel && (
          <div className="modal-section">
            <div className="section-subtitle">指导数据</div>
            <div className="data-panel">
              <div className="data-card">
                <div className="data-label">近30天指导</div>
                <div className="data-value">{tutor.dataPanel.monthlyGuide}人</div>
              </div>
              <div className="data-card">
                <div className="data-label">累计好评</div>
                <div className="data-value highlight">{tutor.dataPanel.totalReviews}条</div>
              </div>
              <div className="data-card">
                <div className="data-label">学员上岸率</div>
                <div className="data-value highlight">{tutor.dataPanel.successRate}%</div>
              </div>
            </div>
          </div>
        )}

        {/* 学员评价 */}
        {tutor.reviews && (
          <div className="modal-section">
            <div className="section-subtitle">学员真实评价</div>
            <div className="review-list">
              {tutor.reviews.map((review, index) => (
                <div key={index} className="review-card">
                  <div className="review-header">
                    <div className="reviewer">{review.reviewer}</div>
                    <div className="review-rating">
                      {'⭐'.repeat(review.rating)}
                    </div>
                  </div>
                  <div className="review-content">{review.content}</div>
                  <div className="review-attach">{review.attachment}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 底部操作栏 */}
        <div className="modal-footer">
          <button className="footer-btn msg" onClick={onMessage}>
            发私信
          </button>
          <button className="footer-btn follow" onClick={onFollow}>
            关注导师
          </button>
        </div>
      </div>
    </div>
  );
};

export default TutorModal; 