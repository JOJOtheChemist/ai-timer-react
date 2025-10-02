import React, { useState, useEffect } from 'react';
import UserTopNav from '../../components/Navbar/UserTopNav';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './SuccessPage.css';
import successService from '../../services/successService';

const SuccessPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilters, setActiveFilters] = useState({
    category: '全部',
    duration: '全部',
    experience: '全部',
    foundation: '全部'
  });
  
  // 真实数据状态
  const [hotCases, setHotCases] = useState([]);
  const [caseList, setCaseList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const USER_ID = 1; // TODO: 从认证系统获取真实用户ID

  // 加载热门案例
  const loadHotCases = async () => {
    try {
      const response = await successService.getHotCases(3);
      // 转换API数据格式
      const formatted = response.map(item => ({
        id: item.id,
        icon: getCategoryIcon(item.category),
        title: item.title,
        tags: item.tags,
        author: item.author_name,
        views: item.views,
        isHot: item.is_hot
      }));
      setHotCases(formatted);
    } catch (error) {
      console.error('加载热门案例失败:', error);
    }
  };

  // 加载案例列表（支持筛选）
  const loadCaseList = async () => {
    try {
      const response = await successService.getCaseList({
        ...activeFilters,
        limit: 20
      });
      
      // 转换API数据格式
      const formatted = response.map(item => ({
        id: item.id,
        icon: getCategoryIcon(item.category),
        title: item.title,
        tags: item.tags,
        author: item.author_name,
        duration: item.duration,
        preview: `免费预览3天`,
        price: `${item.price}钻石查看`
      }));
      
      setCaseList(formatted);
      setTotalCount(formatted.length);
    } catch (error) {
      console.error('加载案例列表失败:', error);
    }
  };

  // 根据分类获取图标
  const getCategoryIcon = (category) => {
    const iconMap = {
      '高考': '📚',
      '考研': '📚',
      '考证': '💼',
      '技能学习': '💻',
      '职场晋升': '🏦'
    };
    return iconMap[category] || '📚';
  };

  // 筛选选项
  const filterOptions = {
    category: ['全部', '高考', '考研', '考证', '技能学习', '职场晋升'],
    duration: ['全部', '＜1000小时', '1000-3000小时', '3000-5000小时', '＞5000小时'],
    experience: ['全部', '失恋逆袭', '在职备考', '早睡早起', '跨专业', '宝妈备考'],
    foundation: ['全部', '0基础', '有基础', '进阶提升']
  };

  const handleFilterChange = (filterType, value) => {
    if (value === '重置筛选') {
      setActiveFilters({
        category: '全部',
        duration: '全部',
        experience: '全部',
        foundation: '全部'
      });
    } else {
      setActiveFilters(prev => ({
        ...prev,
        [filterType]: value
      }));
    }
  };

  // 组件加载时获取数据
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([loadHotCases(), loadCaseList()]);
      setLoading(false);
    };
    loadData();
  }, []);

  // 筛选变化时重新加载案例列表
  useEffect(() => {
    if (!loading) {
      loadCaseList();
    }
  }, [activeFilters]);

  const handleCaseView = (caseId) => {
    console.log('查看案例详情:', caseId);
    // TODO: 导航到案例详情页
  };

  const handleSearch = async (e) => {
    if (e.key === 'Enter' && searchQuery.trim()) {
      try {
        setLoading(true);
        const response = await successService.searchCases(searchQuery);
        // 转换并设置搜索结果
        const formatted = response.map(item => ({
          id: item.id,
          icon: getCategoryIcon(item.category),
          title: item.title,
          tags: item.tags,
          author: item.author_name,
          duration: item.duration,
          preview: `免费预览3天`,
          price: `${item.price}钻石查看`
        }));
        setCaseList(formatted);
        setTotalCount(formatted.length);
      } catch (error) {
        console.error('搜索失败:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  // 加载状态
  if (loading) {
    return (
      <div className="success-page">
        <UserTopNav />
        <main className="success-content">
          <div style={{ 
            textAlign: 'center', 
            padding: '100px 20px',
            color: '#666'
          }}>
            <div style={{ 
              fontSize: '48px', 
              marginBottom: '20px',
              animation: 'spin 2s linear infinite'
            }}>
              ⏳
            </div>
            <div style={{ fontSize: '16px' }}>加载中...</div>
          </div>
        </main>
        <BottomNavBar />
      </div>
    );
  }

  return (
    <div className="success-page">
      <UserTopNav />
      
      <main className="success-content">
        {/* 搜索栏 */}
        <div className="search-bar">
          <i className="search-icon">🔍</i>
          <input 
            type="text" 
            placeholder="搜索目标/时长/经历，如「高考逆袭」「0基础」"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleSearch}
          />
        </div>

        {/* 热门推荐区 */}
        <div className="section-title">热门推荐</div>
        <div className="hot-cases">
          {hotCases.map(hotCase => (
            <div key={hotCase.id} className="case-card-hot" style={{ position: 'relative' }}>
              {hotCase.isHot && <div className="hot-tag">热门</div>}
              <div className="case-img">{hotCase.icon}</div>
              <div className="case-info">
                <div className="case-title">{hotCase.title}</div>
                <div className="case-tags">
                  {hotCase.tags.map((tag, index) => (
                    <span key={index} className="tag">{tag}</span>
                  ))}
                </div>
                <div className="case-meta">
                  <span>上岸者：{hotCase.author}</span>
                  <span>{hotCase.views}人查看</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 筛选区 */}
        <div className="filter-area">
          {/* 目标筛选 */}
          <div className="filter-group">
            <div className="group-title">目标分类</div>
            <div className="filter-tags">
              {filterOptions.category.map(option => (
                <div 
                  key={option}
                  className={`filter-tag ${activeFilters.category === option ? 'active' : ''}`}
                  onClick={() => handleFilterChange('category', option)}
                >
                  {option}
                </div>
              ))}
            </div>
          </div>

          {/* 时长筛选 */}
          <div className="filter-group">
            <div className="group-title">投入时长</div>
            <div className="filter-tags">
              {filterOptions.duration.map(option => (
                <div 
                  key={option}
                  className={`filter-tag ${activeFilters.duration === option ? 'active' : ''}`}
                  onClick={() => handleFilterChange('duration', option)}
                >
                  {option}
                </div>
              ))}
            </div>
          </div>

          {/* 经历筛选 */}
          <div className="filter-group">
            <div className="group-title">特殊经历</div>
            <div className="filter-tags">
              {filterOptions.experience.map(option => (
                <div 
                  key={option}
                  className={`filter-tag ${activeFilters.experience === option ? 'active' : ''}`}
                  onClick={() => handleFilterChange('experience', option)}
                >
                  {option}
                </div>
              ))}
            </div>
          </div>

          {/* 基础筛选 */}
          <div className="filter-group">
            <div className="group-title">初始基础</div>
            <div className="filter-tags">
              {filterOptions.foundation.map(option => (
                <div 
                  key={option}
                  className={`filter-tag ${activeFilters.foundation === option ? 'active' : ''}`}
                  onClick={() => handleFilterChange('foundation', option)}
                >
                  {option}
                </div>
              ))}
              <div 
                className="filter-tag reset"
                onClick={() => handleFilterChange('foundation', '重置筛选')}
              >
                重置筛选
              </div>
            </div>
          </div>
        </div>

        {/* 案例列表区 */}
        <div className="section-title">筛选结果 ({totalCount})</div>
        <div className="case-list">
          {caseList.map(caseItem => (
            <div key={caseItem.id} className="case-card">
              <div className="card-img">{caseItem.icon}</div>
              <div className="card-content">
                <div className="card-title">{caseItem.title}</div>
                <div className="card-tags">
                  {caseItem.tags.map((tag, index) => (
                    <span 
                      key={index} 
                      className={`card-tag ${typeof tag === 'object' && tag.type === 'tutor' ? 'tutor' : ''}`}
                    >
                      {typeof tag === 'object' ? tag.text : tag}
                    </span>
                  ))}
                </div>
                <div className="card-meta">
                  上岸者：{caseItem.author} | 时长：{caseItem.duration} | {caseItem.preview}
                </div>
                <div className="card-actions">
                  <div className="price">{caseItem.price}</div>
                  <button 
                    className="view-btn"
                    onClick={() => handleCaseView(caseItem.id)}
                  >
                    查看详情
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 底部提示 */}
        <div className="bottom-tip">
          上传你的上岸时间表，赢<span>品牌高奢真皮包</span> | 案例均经真人认证，真实可复用
        </div>
      </main>

      <BottomNavBar />
    </div>
  );
};

export default SuccessPage; 