import React, { useState } from 'react';
import UserTopNav from '../../components/Navbar/UserTopNav';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './SuccessPage.css';

const SuccessPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilters, setActiveFilters] = useState({
    category: '全部',
    duration: '1000-3000小时',
    experience: '全部',
    foundation: '全部'
  });

  // 热门推荐案例数据
  const hotCases = [
    {
      id: 1,
      icon: '📚',
      title: '976小时高考逆袭200分上一本',
      tags: ['高考', '失恋逆袭', '日均13h'],
      author: '小夏',
      views: 1286,
      isHot: true
    },
    {
      id: 2,
      icon: '💼',
      title: '4440小时会计学上岸CPA全科',
      tags: ['考证', '在职备考', '3年规划'],
      author: '李会计',
      views: 952,
      isHot: false
    },
    {
      id: 3,
      icon: '💻',
      title: '1800小时0基础逆袭Python开发',
      tags: ['技能', '0基础', '转行'],
      author: '张码农',
      views: 734,
      isHot: false
    }
  ];

  // 案例列表数据
  const caseList = [
    {
      id: 1,
      icon: '📚',
      title: '2100小时考研英语从40分到82分',
      tags: ['考研', '0基础', { text: '认证导师', type: 'tutor' }],
      author: '王老师',
      duration: '2100h',
      preview: '免费预览3天',
      price: '88钻石查看'
    },
    {
      id: 2,
      icon: '🎨',
      title: '1500小时0基础学UI设计入职大厂',
      tags: ['技能学习', '转行', '日均6h'],
      author: '小美学姐',
      duration: '1500h',
      preview: '免费预览3天',
      price: '68钻石查看'
    },
    {
      id: 3,
      icon: '🏦',
      title: '2800小时在职备考银行秋招上岸',
      tags: ['职场晋升', '在职备考', { text: '认证导师', type: 'tutor' }],
      author: '陈经理',
      duration: '2800h',
      preview: '免费预览3天',
      price: '98钻石查看'
    }
  ];

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

  const handleCaseView = (caseId) => {
    console.log('查看案例详情:', caseId);
  };

  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      console.log('搜索:', searchQuery);
    }
  };

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
        <div className="section-title">筛选结果 (12)</div>
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