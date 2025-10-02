import React, { useState, useEffect } from 'react';
import UserTopNav from '../../components/Navbar/UserTopNav';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './TutorPage.css';
import tutorService from '../../services/tutorService';

const TutorPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTutor, setSelectedTutor] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [activeFilters, setActiveFilters] = useState({
    tutorType: ['全部'],
    domain: ['全部'],
    serviceData: ['全部'],
    priceRange: ['全部']
  });
  const [sortBy, setSortBy] = useState('好评优先');
  
  // 真实数据状态
  const [tutors, setTutors] = useState([]);
  const [loading, setLoading] = useState(true);
  const USER_ID = 1; // TODO: 从认证系统获取

  // 旧的硬编码数据（已废弃，仅作参考）
  const _oldTutors = [
    {
      id: 1,
      name: '王英语老师',
      avatar: '👩‍🏫',
      type: 'certified',
      domain: '擅长：考研英语、四六级提分 | 原新东方讲师',
      metrics: {
        rating: 98,
        students: 126,
        successRate: 89
      },
      services: [
        { name: '时间表点评', price: 68 },
        { name: '1v1规划', price: 198 },
        { name: '作文批改', price: 45 }
      ],
      profile: {
        education: '北京外国语大学英语语言文学硕士',
        experience: '考研英语一92分，雅思8.5分',
        work: '新东方考研英语讲师8年，累计授课10000+小时',
        philosophy: '拒绝盲目刷题，用时间管理+技巧拆解提分，尤其擅长基础薄弱学员'
      },
      serviceDetails: [
        {
          name: '时间表点评',
          desc: '12小时内反馈，指出时间分配问题+优化建议',
          price: 68
        },
        {
          name: '1v1学习规划',
          desc: '30分钟语音沟通+定制3个月学习计划+1次后续调整',
          price: 198
        },
        {
          name: '作文批改',
          desc: '逐句批改+语法纠错+思路优化+范文参考',
          price: 45,
          unit: '/篇'
        }
      ],
      dataPanel: {
        monthlyGuide: 18,
        totalReviews: 123,
        successRate: 89
      },
      reviews: [
        {
          reviewer: '小夏（24考研上岸）',
          rating: 5,
          content: '王老师点评时间表太专业了！之前我每天花3小时背单词效率极低，老师建议拆分到碎片时间，省出的时间用来做阅读，英语从58提到76分！',
          attachment: '📅 附：优化后的英语学习时间表（预览）'
        },
        {
          reviewer: '小美（四六级上岸）',
          rating: 5,
          content: '作文批改超级细致，连标点错误都标出来了，还给了适合我的模板，二战六级作文直接从120提到180！',
          attachment: '📝 附：老师修改的作文截图（预览）'
        }
      ]
    },
    {
      id: 2,
      name: '李会计学姐',
      avatar: '👩‍💼',
      type: 'normal',
      domain: '擅长：CPA全科、初级会计 | 四大会计师',
      metrics: {
        rating: 96,
        students: 87,
        successRate: 82
      },
      services: [
        { name: '时间表点评', price: 58 },
        { name: '考点梳理', price: 158 }
      ]
    },
    {
      id: 3,
      name: '张编程导师',
      avatar: '👩‍💻',
      type: 'certified',
      domain: '擅长：Python开发、Web前端 | 大厂工程师',
      metrics: {
        rating: 97,
        students: 93,
        successRate: 85
      },
      services: [
        { name: '项目指导', price: 238 },
        { name: '时间表点评', price: 78 }
      ]
    }
  ];

  // 筛选选项
  const filterOptions = {
    tutorType: ['全部', '普通导师', '认证导师'],
    domain: ['全部', '考研', '会计考证', '语言学习', '编程开发', '公考'],
    serviceData: ['全部', '好评率>95%', '指导学员>50人', '上岸率>80%'],
    priceRange: ['全部', '＜50钻石', '50-100钻石', '100-200钻石', '＞200钻石']
  };

  const sortOptions = ['好评优先', '人气优先', '价格优先'];

  // 处理筛选
  const handleFilterChange = (filterType, value) => {
    if (value === '重置筛选') {
      setActiveFilters({
        tutorType: ['全部'],
        domain: ['全部'],
        serviceData: ['全部'],
        priceRange: ['全部']
      });
      return;
    }

    setActiveFilters(prev => {
      const currentFilters = prev[filterType];
      if (value === '全部') {
        return { ...prev, [filterType]: ['全部'] };
      } else {
        const newFilters = currentFilters.includes('全部') 
          ? [value]
          : currentFilters.includes(value)
            ? currentFilters.filter(f => f !== value)
            : [...currentFilters.filter(f => f !== '全部'), value];
        
        return {
          ...prev,
          [filterType]: newFilters.length === 0 ? ['全部'] : newFilters
        };
      }
    });
  };

  // 处理导师卡片点击
  const handleTutorClick = (tutor) => {
    setSelectedTutor(tutor);
    setShowModal(true);
  };

  // 关闭弹窗
  const closeModal = () => {
    setShowModal(false);
    setSelectedTutor(null);
  };

  // 加载导师列表
  const loadTutors = async () => {
    try {
      const sortByMap = {
        '好评优先': 'rating',
        '经验优先': 'experience',
        '价格优先': 'price'
      };

      const response = await tutorService.getTutorList({
        tutor_type: activeFilters.tutorType.includes('认证导师') && !activeFilters.tutorType.includes('全部') ? 'certified' : null,
        sort_by: sortByMap[sortBy] || 'rating',
        page: 1,
        page_size: 20
      });
      
      // 转换API数据格式
      const formatted = response.map(item => ({
        id: item.id,
        name: item.username || item.name,
        avatar: item.avatar || '👨‍🏫',
        type: item.type === 1 ? 'certified' : 'normal',
        domain: item.domain,
        metrics: {
          rating: item.rating,
          students: item.student_count,
          successRate: item.success_rate
        },
        // 简化的服务数据（实际应该从API获取）
        services: [
          { name: '1v1规划', price: 198 },
          { name: '时间表点评', price: 68 }
        ],
        profile: {
          education: item.education,
          experience: item.experience,
          work: item.work_experience,
          philosophy: item.philosophy
        }
      }));
      
      setTutors(formatted);
    } catch (error) {
      console.error('加载导师列表失败:', error);
    }
  };

  // 处理搜索
  const handleSearch = async (e) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      try {
        setLoading(true);
        const response = await tutorService.searchTutors(searchQuery);
        
        // 转换搜索结果
        const formatted = response.map(item => ({
          id: item.id,
          name: item.username || item.name,
          avatar: item.avatar || '👨‍🏫',
          type: item.type === 1 ? 'certified' : 'normal',
          domain: item.domain,
          metrics: {
            rating: item.rating,
            students: item.student_count,
            successRate: item.success_rate
          },
          services: [
            { name: '1v1规划', price: 198 },
            { name: '时间表点评', price: 68 }
          ],
          profile: {
            education: item.education,
            experience: item.experience,
            work: item.work_experience,
            philosophy: item.philosophy
          }
        }));
        
        setTutors(formatted);
      } catch (error) {
        console.error('搜索失败:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  // 处理服务购买
  const handleServicePurchase = (service) => {
    console.log('购买服务:', service);
  };

  // 处理私信和关注
  const handleMessage = () => {
    console.log('发私信给', selectedTutor?.name);
  };

  const handleFollow = () => {
    console.log('关注导师', selectedTutor?.name);
  };

  // 组件加载时获取数据
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await loadTutors();
      setLoading(false);
    };
    loadData();
  }, []);

  // 筛选和排序变化时重新加载
  useEffect(() => {
    if (!loading) {
      loadTutors();
    }
  }, [activeFilters, sortBy]);

  // 加载状态UI
  if (loading && tutors.length === 0) {
    return (
      <div className="tutor-page">
        <UserTopNav />
        <main className="tutor-content">
          <div style={{ 
            textAlign: 'center', 
            padding: '100px 20px',
            color: '#666'
          }}>
            <div style={{ 
              fontSize: '48px', 
              marginBottom: '20px'
            }}>
              ⏳
            </div>
            <div style={{ fontSize: '16px' }}>加载导师数据中...</div>
          </div>
        </main>
        <BottomNavBar />
      </div>
    );
  }

  return (
    <div className="tutor-page">
      <UserTopNav />
      
      <main className="tutor-content">
        {/* 搜索栏 */}
        <div className="search-bar">
          <i className="search-icon">🔍</i>
          <input 
            type="text" 
            placeholder="搜索导师姓名/擅长领域，如「考研英语」「CPA」"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleSearch}
          />
        </div>

        {/* 筛选区 */}
        <div className="filter-area">
          {/* 导师类型筛选 */}
          <div className="filter-group">
            <div className="group-title">导师类型</div>
            <div className="filter-tags">
              {filterOptions.tutorType.map(option => (
                <div 
                  key={option}
                  className={`filter-tag ${activeFilters.tutorType.includes(option) ? 'active' : ''} ${option === '认证导师' ? 'highlight' : ''}`}
                  onClick={() => handleFilterChange('tutorType', option)}
                >
                  {option}
                </div>
              ))}
            </div>
          </div>

          {/* 擅长领域筛选 */}
          <div className="filter-group">
            <div className="group-title">擅长领域</div>
            <div className="filter-tags">
              {filterOptions.domain.map(option => (
                <div 
                  key={option}
                  className={`filter-tag ${activeFilters.domain.includes(option) ? 'active' : ''}`}
                  onClick={() => handleFilterChange('domain', option)}
                >
                  {option}
                </div>
              ))}
            </div>
          </div>

          {/* 服务数据筛选 */}
          <div className="filter-group">
            <div className="group-title">服务数据</div>
            <div className="filter-tags">
              {filterOptions.serviceData.map(option => (
                <div 
                  key={option}
                  className={`filter-tag ${activeFilters.serviceData.includes(option) ? 'active' : ''}`}
                  onClick={() => handleFilterChange('serviceData', option)}
                >
                  {option}
                </div>
              ))}
            </div>
          </div>

          {/* 价格筛选 */}
          <div className="filter-group">
            <div className="group-title">服务价格</div>
            <div className="filter-tags">
              {filterOptions.priceRange.map(option => (
                <div 
                  key={option}
                  className={`filter-tag ${activeFilters.priceRange.includes(option) ? 'active' : ''}`}
                  onClick={() => handleFilterChange('priceRange', option)}
                >
                  {option}
                </div>
              ))}
              <div 
                className="filter-tag reset"
                onClick={() => handleFilterChange('priceRange', '重置筛选')}
              >
                重置筛选
              </div>
            </div>
          </div>
        </div>

        {/* 排序栏 */}
        <div className="sort-bar">
          <div className="sort-title">找到 {tutors.length} 位导师</div>
          <div className="sort-options">
            {sortOptions.map(option => (
              <div 
                key={option}
                className={`sort-option ${sortBy === option ? 'active' : ''}`}
                onClick={() => setSortBy(option)}
              >
                {option}
              </div>
            ))}
          </div>
        </div>

        {/* 导师列表区 */}
        <div className="tutor-list">
          {tutors.map(tutor => (
            <div 
              key={tutor.id} 
              className="tutor-card"
              onClick={() => handleTutorClick(tutor)}
            >
              <div className="tutor-avatar">{tutor.avatar}</div>
              <div className="tutor-info">
                <div className="tutor-header">
                  <div className="tutor-name">{tutor.name}</div>
                  <div className={`tutor-tag ${tutor.type}`}>
                    {tutor.type === 'certified' ? '认证导师' : '普通导师'}
                  </div>
                </div>
                <div className="tutor-domain">{tutor.domain}</div>
                <div className="tutor-metrics">
                  <div className={`metric-item ${tutor.metrics.rating >= 97 ? 'highlight' : ''}`}>
                    <i>⭐</i> {tutor.metrics.rating}%好评
                  </div>
                  <div className="metric-item">
                    <i>👥</i> {tutor.metrics.students}人指导
                  </div>
                  <div className={`metric-item ${tutor.metrics.successRate >= 85 ? 'highlight' : ''}`}>
                    <i>🎯</i> {tutor.metrics.successRate}%上岸
                  </div>
                </div>
                <div className="tutor-services">
                  {tutor.services.map((service, index) => (
                    <div key={index} className="service-tag">
                      {service.name} {service.price}钻
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 底部提示 */}
        <div className="bottom-tip">
          上传你的上岸时间表，赢<span>品牌高奢真皮包</span> | 导师均经实名认证，服务全程可追溯
        </div>
      </main>

      {/* 导师详情弹窗 */}
      {showModal && selectedTutor && (
        <div className="tutor-modal show" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="close-modal" onClick={closeModal}>×</div>
            
            <div className="modal-header">
              <div className="modal-avatar">{selectedTutor.avatar}</div>
              <div className="modal-header-info">
                <div className="modal-name">{selectedTutor.name}</div>
                <div className={`tutor-tag ${selectedTutor.type}`}>
                  {selectedTutor.type === 'certified' ? '认证导师' : '普通导师'}
                </div>
                <div className="modal-domain">{selectedTutor.domain}</div>
                <div className="modal-metrics">
                  <div className={`modal-metric ${selectedTutor.metrics.rating >= 97 ? 'highlight' : ''}`}>
                    ⭐ {selectedTutor.metrics.rating}%好评
                  </div>
                  <div className="modal-metric">
                    👥 {selectedTutor.metrics.students}人指导
                  </div>
                  <div className={`modal-metric ${selectedTutor.metrics.successRate >= 85 ? 'highlight' : ''}`}>
                    🎯 {selectedTutor.metrics.successRate}%上岸
                  </div>
                </div>
              </div>
            </div>

            {/* 导师Profile */}
            {selectedTutor.profile && (
              <div className="modal-section">
                <div className="section-subtitle">导师Profile</div>
                <div className="profile-content">
                  <p>✅ 教育背景：{selectedTutor.profile.education}</p>
                  <p>✅ 上岸经历：{selectedTutor.profile.experience}</p>
                  <p>✅ 工作经历：{selectedTutor.profile.work}</p>
                  <p>✅ 指导理念：{selectedTutor.profile.philosophy}</p>
                </div>
              </div>
            )}

            {/* 服务列表 */}
            {selectedTutor.serviceDetails && (
              <div className="modal-section">
                <div className="section-subtitle">提供服务</div>
                <div className="service-list">
                  {selectedTutor.serviceDetails.map((service, index) => (
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
                          onClick={() => handleServicePurchase(service)}
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
            {selectedTutor.dataPanel && (
              <div className="modal-section">
                <div className="section-subtitle">指导数据</div>
                <div className="data-panel">
                  <div className="data-card">
                    <div className="data-label">近30天指导</div>
                    <div className="data-value">{selectedTutor.dataPanel.monthlyGuide}人</div>
                  </div>
                  <div className="data-card">
                    <div className="data-label">累计好评</div>
                    <div className="data-value highlight">{selectedTutor.dataPanel.totalReviews}条</div>
                  </div>
                  <div className="data-card">
                    <div className="data-label">学员上岸率</div>
                    <div className="data-value highlight">{selectedTutor.dataPanel.successRate}%</div>
                  </div>
                </div>
              </div>
            )}

            {/* 学员评价 */}
            {selectedTutor.reviews && (
              <div className="modal-section">
                <div className="section-subtitle">学员真实评价</div>
                <div className="review-list">
                  {selectedTutor.reviews.map((review, index) => (
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
              <button className="footer-btn msg" onClick={handleMessage}>
                发私信
              </button>
              <button className="footer-btn follow" onClick={handleFollow}>
                关注导师
              </button>
            </div>
          </div>
        </div>
      )}

      <BottomNavBar />
    </div>
  );
};

export default TutorPage;
