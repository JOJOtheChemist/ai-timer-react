import React, { useState, useEffect } from 'react';
import UserTopNav from '../../components/Navbar/UserTopNav';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './StudyMethodPage.css';
import methodService from '../../services/methodService';

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
  const USER_ID = 1; // TODO: 从认证系统获取

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
  }, []);

  // 筛选变化时重新加载
  useEffect(() => {
    if (!loading) {
      loadMethods();
    }
  }, [activeFilter]);

  // 旧的硬编码数据（已废弃，仅作参考）
  const _oldStudyMethods = [
    {
      id: 1,
      name: '艾宾浩斯复习四步法',
      category: '通用方法',
      type: 'common',
      meta: {
        scope: '全学科',
        checkinCount: 1286
      },
      description: '基于艾宾浩斯遗忘曲线设计，通过4次关键节点复习，将短期记忆转化为长期记忆，尤其适合单词、公式等知识点记忆。',
      steps: [
        '1. 新学后10分钟：快速复盘核心内容（如默写单词词义）',
        '2. 新学后12小时：精读笔记+错题整理（建议睡前完成）',
        '3. 新学后24小时：独立回忆+框架默写',
        '4. 新学后7天：综合刷题+弱点补强'
      ],
      scene: '推荐场景：背单词、记专业课笔记、考证考点记忆',
      stats: {
        rating: 4.9,
        reviews: 328
      }
    },
    {
      id: 2,
      name: '考研英语精读五步法',
      category: '导师独创',
      type: 'tutor',
      meta: {
        tutor: '王英语老师（认证导师）',
        checkinCount: 863
      },
      description: '针对考研英语阅读提分设计，从"词-句-篇-题-复盘"全维度拆解，帮助基础薄弱者从阅读20分提升至35+。',
      steps: [
        '1. 词汇：标注陌生词，结合语境记词义（不查词典先猜）',
        '2. 长难句：拆分语法结构，标注主干和修饰成分',
        '3. 篇章：梳理段落逻辑，画思维导图（3分钟内完成）',
        '4. 做题：重新答题，标注答案定位句',
        '5. 复盘：总结错误类型（如细节题/推理题）及规避方法'
      ],
      scene: '推荐场景：考研英语真题精读、四六级阅读强化',
      stats: {
        rating: 4.8,
        reviews: 215
      }
    },
    {
      id: 3,
      name: '四遍画正字复习法',
      category: '通用方法',
      type: 'common',
      meta: {
        scope: '文科背诵',
        checkinCount: 752
      },
      description: '极简可视化复习法，通过画"正"字记录复习次数，确保每个知识点至少复习4遍，避免漏复习或重复复习。',
      steps: [
        '1. 第1遍：通读教材，在笔记旁画"一"（理解为主）',
        '2. 第2遍：精读+标注重点，画"丨"（记忆关键词）',
        '3. 第3遍：合书回忆，画"丿"（查漏补缺）',
        '4. 第4遍：模拟默写，画"㇏"（完整输出）'
      ],
      scene: '推荐场景：政治大题背诵、专业课论述题、教资考点记忆',
      stats: {
        rating: 4.7,
        reviews: 189
      }
    }
  ];

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
        <div className="ai-recommend">
          <div className="ai-icon">🤖</div>
          <div className="ai-content">
            <div className="ai-title">{aiRecommendation.title}</div>
            <div className="ai-desc">{aiRecommendation.desc}</div>
            <div className="ai-actions">
              <button 
                className="ai-btn primary"
                onClick={() => handleAiRecommendation('use')}
              >
                立即使用
                </button>
              <button 
                className="ai-btn secondary"
                onClick={() => handleAiRecommendation('change')}
              >
                换一个
                </button>
            </div>
            </div>
        </div>

        {/* 分类筛选栏 */}
        <div className="filter-tab">
          {filterOptions.map(option => (
            <button
              key={option}
              className={`filter-type ${activeFilter === option ? 'active' : ''} ${option === '导师独创' ? 'highlight' : ''}`}
              onClick={() => handleFilterChange(option)}
            >
              {option}
                    </button>
          ))}
        </div>

        {/* 方法列表区 */}
        <div className="method-list">
          {studyMethods.map(method => (
            <div key={method.id} className="method-card" data-method={method.id}>
              <div className="method-header">
                <div className="method-info">
                  <div className="method-name">{method.name}</div>
                  <div className="method-meta">
                    <span className={method.meta.tutor ? 'tutor-tag' : ''}>
                      {method.meta.tutor ? method.meta.tutor : `适用：${method.meta.scope}`}
                                    </span>
                    <span>{method.meta.checkinCount}人打卡</span>
                    </div>
                </div>
                <div className={`method-tag ${method.type === 'tutor' ? 'tutor' : ''}`}>
                  {method.category}
            </div>
        </div>

              <div className="method-body">
                <div className="method-desc">{method.description}</div>
                <div className="method-steps">
                  {method.steps.map((step, index) => (
                    <div key={index} className="step-item">{step}</div>
                  ))}
                </div>
                <div className="method-scene">
                  <i>📍</i> {method.scene}
                </div>
            </div>

              <div className="method-footer">
                <div className="method-stats">
                  <div className="stats-item">
                    <i>⭐</i> {method.stats.rating}分
                    </div>
                  <div className="stats-item">
                    <i>💬</i> {method.stats.reviews}条评价
                    </div>
                </div>
                <button 
                  className={`checkin-btn ${method.type === 'tutor' ? 'tutor' : ''}`}
                  onClick={() => handleCheckin(method)}
                >
                  立即打卡
                </button>
                </div>
            </div>
          ))}
        </div>

        {/* 底部提示 */}
        <div className="bottom-tip">
          坚持打卡可获<span>徽章奖励</span> | 导师独创方法可同步至时间表，AI实时优化学习计划
        </div>
    </main>

      {/* 打卡弹窗 */}
      {showCheckinModal && selectedMethod && (
        <div className="checkin-modal show" onClick={closeCheckinModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="icon">
                {selectedMethod.type === 'tutor' ? '👩‍🏫' : '📚'}
        </div>
              <div className="title">{selectedMethod.name} · 打卡</div>
            </div>
            
            <div className="checkin-type">
              {['正字打卡', '计数打卡'].map(type => (
                <div
                  key={type}
                  className={`checkin-option ${checkinType === type ? 'active' : ''}`}
                  onClick={() => handleCheckinTypeChange(type)}
                >
                  {type}
                </div>
              ))}
            </div>
            
            <div className="checkin-content">
              <div className="checkin-count">
                {getCheckinItems().map((item, index) => (
                  <div
                    key={index}
                    className={`checkin-item ${index < checkinProgress ? 'active' : ''}`}
                    onClick={() => handleCheckinProgressChange(index + 1)}
                  >
                    {item}
                            </div>
                ))}
                        </div>
              <textarea
                className="checkin-note"
                placeholder="记录今日复习心得（可选）"
                value={checkinNote}
                onChange={(e) => setCheckinNote(e.target.value)}
              />
            </div>
            
            <div className="modal-actions">
              <button className="modal-btn cancel" onClick={closeCheckinModal}>
                取消
              </button>
              <button className="modal-btn confirm" onClick={handleCompleteCheckin}>
                完成打卡
              </button>
                </div>
            </div>
        </div>
      )}

      <BottomNavBar />
    </div>
  );
};

export default StudyMethodPage; 