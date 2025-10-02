/* eslint-disable */
import React, { useState, useEffect } from 'react';
import UserTopNav from '../../components/Navbar/UserTopNav';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './StudyMethodPage.css';
import methodService from '../../services/methodService';

// 导入子组件
import RecommendCard from './components/RecommendCard/RecommendCard';
import MethodTabs from './components/MethodTabs/MethodTabs';
import MethodCard from './components/MethodCard/MethodCard';
import MethodFooter from './components/MethodFooter/MethodFooter';
import CheckinModal from './components/CheckinModal/CheckinModal';
/* eslint-enable */

const StudyMethodPage = () => {
  const [activeFilter, setActiveFilter] = useState('全部方法');
  const [showCheckinModal, setShowCheckinModal] = useState(false);
  const [selectedMethod, setSelectedMethod] = useState(null);
  const [checkinType, setCheckinType] = useState('正字打卡');
  const [checkinProgress, setCheckinProgress] = useState(1);
  const [checkinNote, setCheckinNote] = useState('');
  
  // 真实数据状态
  const [studyMethods, setStudyMethods] = useState([]);
  const [loading, setLoading] = useState(true);
  // const USER_ID = 1; // TODO: 从认证系统获取
  const USER_ID = 1;

  // AI推荐状态
  const [aiRecommendation, setAiRecommendation] = useState({
    title: '为你推荐 · 基于你的时间表分析',
    desc: '发现你复习频率低，推荐「艾宾浩斯复习四步法」，已帮助326人提升记忆效率'
  });
  
  // 加载学习方法数据
  const loadMethods = async () => {
    try {
      setLoading(true);
      const filters = {
        user_id: USER_ID,
        page: 1,
        page_size: 20
      };
      
      // 如果有分类筛选，添加category参数
      if (activeFilter !== '全部方法') {
        const categoryMap = {
          '通用方法': 'common',
          '导师独创': 'tutor'
        };
        filters.category = categoryMap[activeFilter];
      }
      
      const methods = await methodService.getMethodList(filters);
      
      // 转换数据格式以匹配组件期望的格式
      const formatted = methods.map(method => ({
        id: method.id,
        name: method.name,
        category: method.category === 'common' ? '通用方法' : '导师独创',
        type: method.category,
        meta: {
          scope: method.meta.scope || method.type,
          tutor: method.meta.tutor,
          checkinCount: method.meta.checkinCount
        },
        description: method.description,
        steps: method.steps,
        scene: method.scene,
        stats: {
          rating: method.stats.rating,
          reviews: method.stats.reviews
        }
      }));
      
      setStudyMethods(formatted);
    } catch (error) {
      console.error('加载学习方法失败，使用示例数据:', error);
      // API失败时使用示例数据
      setStudyMethods([
        {
          id: 1,
          name: '艾宾浩斯复习四步法',
          category: '通用方法',
          type: 'common',
          meta: {
            scope: '记忆类',
            tutor: null,
            checkinCount: 3254
          },
          description: '基于艾宾浩斯遗忘曲线设计，通过4次关键节点复习，将短期记忆转化为长期记忆，尤其适合单词、公式等知识点记忆。',
          steps: [
            '第1次复习：学习后5-10分钟立即回顾',
            '第2次复习：学习后1小时复习',
            '第3次复习：学习后1天复习',
            '第4次复习：学习后2天、4天、7天、15天循环复习'
          ],
          scene: '英语单词、数学公式、专业术语等需要大量记忆的学习场景',
          stats: {
            rating: 4.8,
            reviews: 1234
          }
        },
        {
          id: 2,
          name: '番茄工作法',
          category: '通用方法',
          type: 'common',
          meta: {
            scope: '时间管理',
            tutor: null,
            checkinCount: 5678
          },
          description: '将工作时间分成25分钟的专注时段，每个时段后休息5分钟。完成4个番茄钟后，休息15-30分钟。',
          steps: [
            '设定25分钟计时器，开始专注学习',
            '番茄钟结束后，休息5分钟',
            '重复4次后，进行15-30分钟的长休息',
            '记录完成的番茄钟数量'
          ],
          scene: '适合需要长时间专注的学习任务，如做题、阅读等',
          stats: {
            rating: 4.7,
            reviews: 2345
          }
        },
        {
          id: 3,
          name: '费曼学习法',
          category: '通用方法',
          type: 'common',
          meta: {
            scope: '理解类',
            tutor: null,
            checkinCount: 2156
          },
          description: '通过向他人讲解的方式检验自己是否真正理解了知识点，发现理解漏洞后回到教材深入学习。',
          steps: [
            '选择一个要学习的概念',
            '假装向一个完全不懂的人讲解这个概念',
            '发现讲解中的卡壳点，回到教材深入学习',
            '简化语言，用类比和例子帮助理解'
          ],
          scene: '适合理解复杂概念、原理性知识，如数学定理、专业课理论等',
          stats: {
            rating: 4.9,
            reviews: 1567
          }
        }
      ]);
    } finally {
      setLoading(false);
    }
  };
  
  // 初始加载
  useEffect(() => {
    loadMethods();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 筛选变化时重新加载
  useEffect(() => {
    if (!loading) {
      loadMethods();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeFilter]);



  // 筛选选项
  const filterOptions = ['全部方法', '通用方法', '导师独创', '考研专属', '考证必备', '语言学习'];

  // 处理筛选
  const handleFilterChange = (filter) => {
    setActiveFilter(filter);
  };

  // 处理打卡
  const handleCheckin = (method) => {
    setSelectedMethod(method);
    setShowCheckinModal(true);
    setCheckinProgress(1);
    setCheckinNote('');
  };

  // 关闭打卡弹窗
  const closeCheckinModal = () => {
    setShowCheckinModal(false);
    setSelectedMethod(null);
  };

  // 处理打卡类型切换
  const handleCheckinTypeChange = (type) => {
    setCheckinType(type);
    setCheckinProgress(1);
  };

  // 处理打卡进度
  const handleCheckinProgressChange = (progress) => {
    setCheckinProgress(progress);
  };

  // 完成打卡
  const handleCompleteCheckin = async () => {
    try {
      const checkinData = {
        checkin_type: checkinType,
        progress: checkinProgress,
        note: checkinNote.trim()
      };
      
      await methodService.submitCheckin(selectedMethod.id, checkinData, USER_ID);
      
      const note = checkinNote.trim() ? '，心得已保存' : '';
      alert(`打卡成功！已完成${checkinProgress}遍复习${note}，同步至你的个人动态~`);
      
      closeCheckinModal();
      // 重新加载数据以更新打卡人数
      loadMethods();
    } catch (error) {
      console.error('打卡失败:', error);
      alert('打卡失败，请稍后重试');
    }
  };

  // 处理AI推荐
  const handleAiRecommendation = (action) => {
    if (action === 'use') {
      // 跳转到对应方法
      const targetMethod = document.querySelector('[data-method="1"]');
      if (targetMethod) {
        targetMethod.scrollIntoView({ behavior: 'smooth' });
      }
    } else {
      // 切换推荐
      setAiRecommendation({
        title: '为你推荐 · 基于你的时间表分析',
        desc: '发现你英语阅读耗时过长，推荐「考研英语精读五步法」，王英语老师独创，863人打卡提分'
      });
    }
  };

  // 获取打卡显示内容
  const getCheckinItems = () => {
    if (checkinType === '正字打卡') {
      return ['一', '丨', '丿', '㇏'];
    } else {
      return ['1', '2', '3', '4'];
    }
  };

  // 加载状态UI
  if (loading) {
    return (
      <div className="study-method-page">
        <UserTopNav />
        <main className="study-method-content">
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '400px',
            fontSize: '18px',
            color: '#666'
          }}>
            加载中...
          </div>
        </main>
        <BottomNavBar />
      </div>
    );
  }

  return (
    <div className="study-method-page">
      <UserTopNav />
      
      <main className="study-method-content">
        {/* AI推荐区 */}
        <RecommendCard
          recommendation={aiRecommendation}
          onUse={() => handleAiRecommendation('use')}
          onChange={() => handleAiRecommendation('change')}
        />

        {/* 分类筛选栏 */}
        <MethodTabs
          filterOptions={filterOptions}
          activeFilter={activeFilter}
          onFilterChange={handleFilterChange}
        />

        {/* 方法列表区 */}
        <div className="method-list">
          {studyMethods.map(method => (
            <MethodCard
              key={method.id}
              method={method}
              onCheckin={handleCheckin}
            />
          ))}
        </div>

        {/* 底部提示 */}
        <MethodFooter />
      </main>

      {/* 打卡弹窗 */}
      <CheckinModal
        show={showCheckinModal}
        method={selectedMethod}
        checkinType={checkinType}
        checkinProgress={checkinProgress}
        checkinNote={checkinNote}
        onClose={closeCheckinModal}
        onTypeChange={handleCheckinTypeChange}
        onProgressChange={handleCheckinProgressChange}
        onNoteChange={setCheckinNote}
        onComplete={handleCompleteCheckin}
        getCheckinItems={getCheckinItems}
      />

      <BottomNavBar />
    </div>
  );
};

export default StudyMethodPage; 