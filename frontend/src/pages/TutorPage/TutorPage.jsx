import React, { useState, useEffect } from 'react';
import UserTopNav from '../../components/Navbar/UserTopNav';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './TutorPage.css';
import tutorService from '../../services/tutorService';

// 导入子组件
import {
  TutorSearch,
  FilterPanel,
  SortBar,
  TutorList,
  TutorFooter,
  TutorModal
} from './components';

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
  // const USER_ID = 1; // TODO: 从认证系统获取

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
      console.error('加载导师列表失败，使用示例数据:', error);
      // API失败时使用示例数据
      setTutors([
        {
          id: 1,
          name: '王英语老师',
          avatar: '👨‍🏫',
          type: 'certified',
          domain: '考研英语',
          metrics: { rating: 4.9, students: 256, successRate: 89 },
          services: [
            { name: '1v1规划', price: 198 },
            { name: '时间表点评', price: 68 }
          ],
          profile: {
            education: '北京外国语大学 英语专业硕士',
            experience: '8年考研英语教学经验，累计帮助500+学员上岸',
            work: '某知名教育机构首席英语讲师',
            philosophy: '授人以鱼不如授人以渔，我会教你如何高效学习英语'
          }
        },
        {
          id: 2,
          name: '李数学导师',
          avatar: '👩‍🏫',
          type: 'certified',
          domain: '考研数学',
          metrics: { rating: 4.8, students: 198, successRate: 85 },
          services: [
            { name: '1v1规划', price: 198 },
            { name: '时间表点评', price: 68 }
          ],
          profile: {
            education: '清华大学 数学系博士',
            experience: '6年考研数学辅导经验',
            work: '高校数学教师',
            philosophy: '数学不难，找对方法最重要'
          }
        },
        {
          id: 3,
          name: '张专业课学长',
          avatar: '👨‍🎓',
          type: 'normal',
          domain: '计算机专业课',
          metrics: { rating: 4.7, students: 89, successRate: 82 },
          services: [
            { name: '1v1规划', price: 158 },
            { name: '时间表点评', price: 58 }
          ],
          profile: {
            education: '浙江大学 计算机专业硕士',
            experience: '刚上岸，愿意分享经验',
            work: '互联网大厂工程师',
            philosophy: '用最短的时间掌握最核心的知识点'
          }
        }
      ]);
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
        console.error('搜索失败，显示空结果:', error);
        setTutors([]);
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 筛选和排序变化时重新加载
  useEffect(() => {
    if (!loading) {
      loadTutors();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
        <TutorSearch
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSearch={handleSearch}
        />

        {/* 筛选区 */}
        <FilterPanel
          filterOptions={filterOptions}
          activeFilters={activeFilters}
          onFilterChange={handleFilterChange}
        />

        {/* 排序栏 */}
        <SortBar
          sortOptions={sortOptions}
          sortBy={sortBy}
          onSortChange={setSortBy}
          tutorCount={tutors.length}
        />

        {/* 导师列表 */}
        <TutorList
          tutors={tutors}
          onTutorClick={handleTutorClick}
        />

        {/* 底部提示 */}
        <TutorFooter />
      </main>

      {/* 导师详情弹窗 */}
      <TutorModal
        show={showModal}
        tutor={selectedTutor}
        onClose={closeModal}
        onServicePurchase={handleServicePurchase}
        onMessage={handleMessage}
        onFollow={handleFollow}
      />

      <BottomNavBar />
    </div>
  );
};

export default TutorPage;
