import React, { useState, useEffect } from 'react';
import UserTopNav from '../../components/Navbar/UserTopNav';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import './MainSchedulePage.css';
import scheduleService from '../../services/scheduleService';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

const MainSchedulePage = () => {
  const [expandedTasks, setExpandedTasks] = useState({});
  const [activeFilter, setActiveFilter] = useState("全部");
  const [showFullStats, setShowFullStats] = useState(false);
  const [quickInput, setQuickInput] = useState("");
  const [selectedMoods, setSelectedMoods] = useState({});
  const [aiRecommendations, setAiRecommendations] = useState({});
  
  // 真实数据状态
  const [tasks, setTasks] = useState([]);
  const [timeSlots, setTimeSlots] = useState([]);
  const [scheduleOverview, setScheduleOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const USER_ID = 1; // TODO: 从认证系统获取真实用户ID

  const toggleTaskExpansion = (taskId) => {
    setExpandedTasks(prev => ({
      ...prev,
      [taskId]: !prev[taskId]
    }));
  };

  const handleMoodSelect = (slotId, mood) => {
    setSelectedMoods(prev => ({
      ...prev,
      [slotId]: prev[slotId] === mood ? null : mood
    }));
  };

  const handleAiRecommendation = (id, accept) => {
    setAiRecommendations(prev => ({
      ...prev,
      [id]: accept
    }));
  };

  const handleQuickAdd = async () => {
    if (quickInput.trim()) {
      try {
        console.log('快速添加任务:', quickInput);
        await scheduleService.quickAddTask(quickInput, USER_ID);
        setQuickInput("");
        // 重新加载任务列表
        await loadTasks();
      } catch (error) {
        console.error('添加任务失败:', error);
        alert('添加任务失败，请重试');
      }
    }
  };

  const handleFilterClick = (filter) => {
    setActiveFilter(filter);
  };

  // 加载任务列表
  const loadTasks = async () => {
    try {
      const response = await scheduleService.getTaskList({ user_id: USER_ID });
      const apiTasks = response.tasks || [];
      
      // 转换API数据格式为组件需要的格式
      const formattedTasks = apiTasks.map(task => ({
        id: task.id,
        name: task.name,
        type: task.type,
        category: task.category || task.type,
        weeklyHours: parseFloat(task.weekly_hours) || 0,
        isHighFrequency: task.is_high_frequency,
        isOvercome: task.is_overcome,
        expanded: false,
        subTasks: (task.subtasks || []).map(subtask => ({
          id: subtask.id,
          name: subtask.name,
          hours: parseFloat(subtask.hours) || 0,
          isHighFrequency: subtask.is_high_frequency,
          isOvercome: subtask.is_overcome
        }))
      }));
      
      setTasks(formattedTasks);
    } catch (error) {
      console.error('❌ 加载任务失败:', error);
      setError('加载任务失败');
    }
  };

  // 加载今日时间表
  const loadTimeSlots = async () => {
    try {
      const response = await scheduleService.getTodayTimeSlots(USER_ID);
      const apiSlots = response.time_slots || [];
      
      // 转换API数据格式
      const formattedSlots = apiSlots.map(slot => ({
        id: slot.id,
        time: slot.time_range,
        task: slot.task_name || '空闲时间',
        type: slot.task_type || 'life',
        category: slot.task_type || '空闲',
        status: slot.status,
        isHighFrequency: slot.is_high_frequency || false,
        isOvercome: slot.is_overcome || false,
        isAIRecommended: slot.is_ai_recommended,
        note: slot.note,
        aiTip: slot.ai_tip,
        mood: slot.mood
      }));
      
      setTimeSlots(formattedSlots);
      setScheduleOverview(response.overview);
      
      console.log('✅ 数据加载成功:', {
        任务数: formattedSlots.length,
        概览: response.overview
      });
    } catch (error) {
      console.error('❌ 加载时间表失败:', error);
      setError('加载时间表失败');
    }
  };

  // 组件加载时获取数据
  useEffect(() => {
    const loadAllData = async () => {
      setLoading(true);
      try {
        await Promise.all([loadTasks(), loadTimeSlots()]);
      } catch (error) {
        console.error('加载数据失败:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadAllData();
  }, []);

  // 计算统计数据（从真实API数据）
  const stats = scheduleOverview ? [
    { 
      title: "总学习时长", 
      value: `${scheduleOverview.total_study_hours || 0}h`, 
      color: "text-study" 
    },
    { 
      title: "已完成", 
      value: `${scheduleOverview.completed_slots || 0}/${scheduleOverview.total_slots || 0}`, 
      color: "text-frequent" 
    },
    { 
      title: "完成率", 
      value: `${(scheduleOverview.completion_rate || 0).toFixed(1)}%`, 
      color: "text-warning" 
    },
    { 
      title: "进行中", 
      value: `${scheduleOverview.in_progress_slots || 0}`, 
      color: "text-ai" 
    }
  ] : [
    { title: "总学习时长", value: "0h", color: "text-study" },
    { title: "已完成", value: "0/0", color: "text-frequent" },
    { title: "完成率", value: "0%", color: "text-warning" },
    { title: "进行中", value: "0", color: "text-ai" }
  ];

  // 图表数据
  const weeklyChartData = {
    labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    datasets: [
      {
        label: '学习',
        data: [1.5, 2, 0, 1.5, 3.5, 0, 0],
        backgroundColor: '#3b82f6',
        borderRadius: 3
      },
      {
        label: '生活',
        data: [1, 1, 0, 1, 2, 0, 0],
        backgroundColor: '#10b981',
        borderRadius: 3
      },
      {
        label: '工作',
        data: [0, 0, 2, 2, 0, 0, 0],
        backgroundColor: '#6366f1',
        borderRadius: 3
      }
    ]
  };

  const doughnutChartData = {
    labels: ['学习', '生活', '工作', '玩乐'],
    datasets: [
      {
        data: [8.5, 5, 4, 2],
        backgroundColor: ['#3b82f6', '#10b981', '#6366f1', '#f59e0b'],
        borderWidth: 0
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { stacked: true },
      y: { 
        stacked: true, 
        beginAtZero: true,
        title: { display: true, text: '时长(小时)', font: { size: 10 } }
      }
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: { boxWidth: 8, padding: 10, font: { size: 10 } }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: { boxWidth: 10, padding: 15, font: { size: 11 } }
      }
    }
  };

  const getTaskColor = (type) => {
    const colorMap = {
      'study': 'study',
      'life': 'life',
      'work': 'work',
      'play': 'play'
    };
    return colorMap[type] || 'gray';
  };



  const getStatusIcon = (status) => {
    const iconMap = {
      'completed': 'fa-check-circle',
      'in-progress': 'fa-clock-o',
      'pending': 'fa-hourglass-half',
      'empty': 'fa-plus-circle'
    };
    return iconMap[status] || 'fa-circle-o';
  };

  const getStatusColor = (status) => {
    const colorMap = {
      'completed': 'text-green-500',
      'in-progress': 'text-blue-500',
      'pending': 'text-yellow-500',
      'empty': 'text-gray-400'
    };
    return colorMap[status] || 'text-gray-500';
  };

  const getMoodIcon = (mood) => {
    const iconMap = {
      'happy': 'fa-smile-o',
      'focused': 'fa-eye',
      'tired': 'fa-tired'
    };
    return iconMap[mood] || 'fa-plus';
  };

  const getMoodStyle = (mood, isSelected) => {
    const baseStyle = "w-5 h-5 rounded-full flex items-center justify-center text-xs transition-colors";
    if (isSelected) {
      const selectedStyles = {
        'happy': 'bg-yellow-100 text-yellow-500',
        'focused': 'bg-blue-100 text-blue-500',
        'tired': 'bg-red-100 text-red-500'
      };
      return `${baseStyle} ${selectedStyles[mood] || 'bg-gray-100 text-gray-500'}`;
    }
    return `${baseStyle} bg-gray-100 text-gray-500 hover:bg-${mood === 'happy' ? 'yellow' : mood === 'focused' ? 'blue' : 'red'}-100`;
  };

  // 加载状态
  if (loading) {
    return (
      <div className="main-schedule-page bg-gray-50 font-sans text-gray-800">
        <UserTopNav />
        <main className="px-4 py-3 pb-24">
          <div className="flex items-center justify-center h-screen">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-gray-600">加载中...</p>
            </div>
          </div>
        </main>
        <BottomNavBar />
      </div>
    );
  }

  // 错误状态
  if (error) {
    return (
      <div className="main-schedule-page bg-gray-50 font-sans text-gray-800">
        <UserTopNav />
        <main className="px-4 py-3 pb-24">
          <div className="flex items-center justify-center h-screen">
            <div className="text-center">
              <div className="text-red-500 text-5xl mb-4">⚠️</div>
              <p className="text-gray-800 text-lg mb-2">加载失败</p>
              <p className="text-gray-600 mb-4">{error}</p>
              <button 
                onClick={() => window.location.reload()} 
                className="bg-primary text-white px-6 py-2 rounded-lg hover:bg-primary/90"
              >
                重新加载
              </button>
            </div>
          </div>
        </main>
        <BottomNavBar />
      </div>
    );
  }

  return (
    <div className="main-schedule-page bg-gray-50 font-sans text-gray-800">
      <UserTopNav />
      
      <main className="px-4 py-3 pb-24">
        {/* 进度概览 */}
        <div className="bg-white rounded-xl shadow-sm p-3 mb-3">
          <div className="flex flex-wrap justify-between items-center gap-2">
            <div>
              <div className="text-sm font-medium">2025年9月19日 星期五</div>
              <div className="text-xs text-gray-500">9月第3周 · 已完成 3/8 任务</div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm font-medium text-primary">本周进度 38%</div>
                <div className="w-24 h-1.5 bg-gray-100 rounded-full mt-1">
                  <div className="h-1.5 bg-primary rounded-full" style={{width: '38%'}}></div>
                </div>
              </div>
              <button className="text-xs bg-primary/10 text-primary px-2.5 py-1 rounded-full">
                周视图
              </button>
            </div>
          </div>
        </div>

        {/* 核心功能区：任务列表 + 时间表 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 mb-4">
          {/* 左侧：任务列表 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm p-3 h-full">
              {/* 标签筛选 */}
              <div className="flex gap-2 mb-3 overflow-x-auto scrollbar-thin pb-1">
                {[
                  { key: '全部', label: '全部', color: 'primary' },
                  { key: 'study', label: '学习', icon: 'fa-book', color: 'study' },
                  { key: 'life', label: '生活', icon: 'fa-home', color: 'life' },
                  { key: 'play', label: '玩乐', icon: 'fa-gamepad', color: 'play' },
                  { key: 'work', label: '工作', icon: 'fa-briefcase', color: 'work' }
                ].map(filter => (
                  <button
                    key={filter.key}
                    onClick={() => handleFilterClick(filter.key)}
                    className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                      activeFilter === filter.key
                        ? `bg-${filter.color} text-white`
                        : `bg-${filter.color}/10 text-${filter.color}`
                    }`}
                  >
                    {filter.icon && <i className={`fa ${filter.icon} mr-1`}></i>}
                    {filter.label}
                  </button>
                ))}
              </div>

              {/* 任务搜索和筛选 */}
              <div className="flex gap-2 mb-3">
                <div className="relative flex-1">
                  <input 
                    type="text" 
                    placeholder="搜索任务..." 
                    className="w-full pl-8 pr-3 py-1.5 bg-gray-50 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                  <i className="fa fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm"></i>
                </div>
                <button className="bg-gray-100 hover:bg-gray-200 p-1.5 rounded-lg text-gray-500">
                  <i className="fa fa-filter"></i>
                </button>
              </div>

              {/* 任务列表标题 */}
              <div className="flex justify-between items-center mb-2">
                <h2 className="font-medium text-sm">高频任务库</h2>
                <button className="text-xs text-primary">
                  <i className="fa fa-plus mr-1"></i> 新增
                </button>
              </div>

              {/* 任务标记说明 */}
              <div className="flex gap-3 mb-2 text-xs text-gray-500">
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-frequent rounded-full mr-1"></span>
                  <span>高频</span>
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-warning rounded-full mr-1"></span>
                  <span>待克服</span>
                </div>
                <div className="flex items-center">
                  <span className="w-2 h-2 bg-gray-300 rounded-full mr-1"></span>
                  <span>本周时长</span>
                </div>
              </div>

              {/* 任务列表 */}
              <div className="space-y-1 max-h-[400px] overflow-y-auto scrollbar-thin pr-1">
                {tasks.map(task => (
                  <div key={task.id} className={`border-l-2 border-${getTaskColor(task.type)} pl-2 py-1`}>
                    <div className="task-item hover:bg-gray-50 transition-colors flex justify-between items-center p-1.5 rounded cursor-pointer"
                         onClick={() => task.subTasks.length > 0 && toggleTaskExpansion(task.id)}>
                      <div className="flex items-center">
                        {task.subTasks.length > 0 ? (
                          <i className={`fa ${expandedTasks[task.id] ? 'fa-chevron-down' : 'fa-chevron-right'} text-xs text-gray-400 mr-2 transition-transform duration-200`}></i>
                        ) : (
                          <i className="fa fa-circle-o text-xs text-gray-400 mr-2"></i>
                        )}
                        <span className="text-sm">{task.name}</span>
                        <span className={`ml-2 bg-${getTaskColor(task.type)}/10 text-${getTaskColor(task.type)} text-xs px-1.5 py-0.5 rounded`}>
                          {task.category}
                        </span>
                        {task.isHighFrequency && (
                          <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-frequent text-white text-xs rounded-full">
                            <i className="fa fa-bolt"></i>
                          </span>
                        )}
                        {task.isOvercome && (
                          <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-warning text-white text-xs rounded-full">
                            <i className="fa fa-exclamation"></i>
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-gray-500">
                        {task.weeklyHours}h
                      </div>
                    </div>
                    
                    {/* 子任务 */}
                    {task.subTasks.length > 0 && expandedTasks[task.id] && (
                      <div className="pl-4 mt-1 space-y-1">
                        {task.subTasks.map(subTask => (
                          <div key={subTask.id} className="task-item hover:bg-gray-50 transition-colors flex justify-between items-center p-1.5 rounded">
                            <div className="flex items-center">
                              <i className="fa fa-circle-o text-xs text-gray-400 mr-2"></i>
                              <span className="text-sm">{subTask.name}</span>
                              {subTask.isHighFrequency && (
                                <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-frequent text-white text-xs rounded-full">
                                  <i className="fa fa-bolt"></i>
                                </span>
                              )}
                              {subTask.isOvercome && (
                                <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-warning text-white text-xs rounded-full">
                                  <i className="fa fa-exclamation"></i>
                                </span>
                              )}
                            </div>
                            <div className="text-xs text-gray-500">
                              {subTask.hours}h
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 右侧：时间表 */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm p-3 h-full">
              <div className="flex justify-between items-center mb-3">
                <h2 className="font-medium text-sm">今日时间表</h2>
                <div className="flex gap-2">
                  <button className="text-xs text-gray-500 hover:text-primary">
                    <i className="fa fa-refresh mr-1"></i> 重置
                  </button>
                  <button className="text-xs bg-ai/10 text-ai">
                    <i className="fa fa-magic mr-1"></i> AI规划
                  </button>
                </div>
              </div>

              {/* 时间表内容 */}
              <div className="space-y-2 max-h-[400px] overflow-y-auto scrollbar-thin pr-1">
                {timeSlots.map(slot => (
                  <div key={slot.id} className={`time-slot border rounded-lg p-2 transition-colors ${
                    slot.isAIRecommended 
                      ? 'border-ai/30 bg-ai/5' 
                      : slot.status === 'in-progress'
                      ? 'border-primary/30 bg-primary/5'
                      : slot.status === 'empty'
                      ? 'border-dashed border-gray-200 hover:border-primary/30 hover:bg-gray-50'
                      : 'border-gray-100 hover:border-primary/30'
                  }`}>
                    <div className="flex justify-between">
                      <div className="w-20 text-xs text-gray-500">{slot.time}</div>
                      <div className="flex gap-1">
                        {/* 心情标记按钮组 */}
                        {['happy', 'focused', 'tired'].map(mood => (
                          <button
                            key={mood}
                            onClick={() => handleMoodSelect(slot.id, mood)}
                            className={getMoodStyle(mood, selectedMoods[slot.id] === mood)}
                            title={mood === 'happy' ? '愉快' : mood === 'focused' ? '专注' : '疲惫'}
                          >
                            <i className={`fa ${getMoodIcon(mood)}`}></i>
                          </button>
                        ))}
                        {!slot.task && (
                          <button className="w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center text-xs text-gray-500 hover:bg-gray-200" title="添加心情">
                            <i className="fa fa-plus"></i>
                          </button>
                        )}
                      </div>
                    </div>
                    
                    {slot.task ? (
                      <div className="mt-1 flex items-start">
                        <div className="w-20"></div>
                        <div className="flex-1">
                          <div className="flex items-center">
                            <span className="text-sm font-medium">{slot.task}</span>
                            <span className={`ml-2 bg-${getTaskColor(slot.type)}/10 text-${getTaskColor(slot.type)} text-xs px-1.5 py-0.5 rounded`}>
                              {slot.category}
                            </span>
                            {slot.isHighFrequency && (
                              <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-frequent text-white text-xs rounded-full">
                                <i className="fa fa-bolt"></i>
                              </span>
                            )}
                            {slot.isOvercome && (
                              <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-warning text-white text-xs rounded-full">
                                <i className="fa fa-exclamation"></i>
                              </span>
                            )}
                            {slot.isAIRecommended && (
                              <span className="ml-1.5 inline-flex items-center justify-center w-4 h-4 bg-ai text-white text-xs rounded-full">
                                <i className="fa fa-robot"></i>
                              </span>
                            )}
                          </div>
                          <div className="text-xs mt-0.5">
                            <i className={`fa ${getStatusIcon(slot.status)} ${getStatusColor(slot.status)} mr-1`}></i>
                            {slot.status === 'completed' ? '已完成' : 
                             slot.status === 'in-progress' ? '进行中' : 
                             slot.status === 'pending' ? '未开始' : ''}
                          </div>
                          
                          {/* 任务备注 */}
                          {slot.note && (
                            <div className="mt-1 text-xs bg-gray-50 p-2 rounded border border-gray-100">
                              <div className="text-gray-500 mb-0.5">备注：</div>
                              <div className="text-gray-700">{slot.note}</div>
                            </div>
                          )}
                          
                          {/* AI推荐 */}
                          {slot.aiTip && (
                            <div className="mt-1 flex items-center text-xs bg-ai/10 p-2 rounded border border-ai/20">
                              <i className="fa fa-lightbulb-o text-ai mr-1.5"></i>
                              <span className="flex-1">AI推荐：{slot.aiTip}</span>
                              <div className="flex gap-1 ml-1">
                                <button 
                                  onClick={() => handleAiRecommendation(slot.id, true)}
                                  className={`w-5 h-5 rounded-full flex items-center justify-center text-xs transition-colors ${
                                    aiRecommendations[slot.id] === true
                                      ? 'bg-ai text-white'
                                      : 'bg-white border border-ai/30 text-ai hover:bg-ai hover:text-white'
                                  }`}
                                >
                                  <i className="fa fa-check"></i>
                                </button>
                                <button 
                                  onClick={() => handleAiRecommendation(slot.id, false)}
                                  className={`w-5 h-5 rounded-full flex items-center justify-center text-xs transition-colors ${
                                    aiRecommendations[slot.id] === false
                                      ? 'bg-gray-100'
                                      : 'bg-white border border-gray-300 text-gray-500 hover:bg-gray-100'
                                  }`}
                                >
                                  <i className="fa fa-times"></i>
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="mt-1 flex items-start">
                        <div className="w-20"></div>
                        <div className="flex-1">
                          <div className="text-sm text-gray-400 mb-1">
                            <i className="fa fa-plus-circle mr-1"></i> 点击添加任务
                          </div>
                          {/* AI推荐任务 */}
                          {slot.aiTip && (
                            <div className="mt-1 flex items-center text-xs bg-ai/10 p-2 rounded border border-ai/20">
                              <i className="fa fa-lightbulb-o text-ai mr-1.5"></i>
                              <span className="flex-1">AI推荐：{slot.aiTip}</span>
                              <div className="flex gap-1 ml-1">
                                <button 
                                  onClick={() => handleAiRecommendation(slot.id, true)}
                                  className="w-5 h-5 rounded-full bg-white border border-ai/30 flex items-center justify-center text-ai hover:bg-ai hover:text-white transition-colors"
                                >
                                  <i className="fa fa-check text-xs"></i>
                                </button>
                                <button 
                                  onClick={() => handleAiRecommendation(slot.id, false)}
                                  className="w-5 h-5 rounded-full bg-white border border-gray-300 flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors"
                                >
                                  <i className="fa fa-times text-xs"></i>
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 快捷输入区 */}
        <div className="bg-white rounded-xl shadow-sm p-3 mb-4">
          <div className="flex gap-2">
            <button className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 hover:bg-primary hover:text-white transition-colors">
              <i className="fa fa-microphone"></i>
            </button>
            <input 
              type="text" 
              placeholder="添加任务备注或对AI说..." 
              value={quickInput}
              onChange={(e) => setQuickInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleQuickAdd()}
              className="flex-1 px-3 py-2 bg-gray-50 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            />
            <button 
              onClick={handleQuickAdd}
              className="px-4 py-2 bg-primary text-white rounded-lg text-sm hover:bg-primary/90 transition-colors"
            >
              确认
            </button>
          </div>
        </div>

        {/* 统计分析区 */}
        <div className="space-y-3 mb-20">
          {/* 本周统计概览 */}
          <div className="bg-white rounded-xl shadow-sm p-3">
            <div className="flex justify-between items-center mb-3">
              <h2 className="font-medium text-sm">本周统计概览</h2>
              <button 
                onClick={() => setShowFullStats(true)}
                className="text-xs text-primary"
              >
                查看完整统计 →
              </button>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
              {stats.map((stat, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-2">
                  <div className="text-xs text-gray-500">{stat.title}</div>
                  <div className={`text-lg font-bold ${stat.color}`}>{stat.value}</div>
                </div>
              ))}
            </div>
            
            {/* 本周时间分布图表 */}
            <div className="h-[160px]">
              <Bar data={weeklyChartData} options={chartOptions} />
            </div>
          </div>

          {/* 行为分析 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* 心情-任务相关性分析 */}
            <div className="bg-white rounded-xl shadow-sm p-3">
              <div className="flex justify-between items-center mb-2">
                <h2 className="font-medium text-sm">心情-效率分析</h2>
                <button className="text-xs text-primary">详情</button>
              </div>
              <div className="text-xs text-gray-600 space-y-1.5">
                <p>• 专注状态下完成高频任务效率提升42%</p>
                <p>• 数学类任务在心情愉快时正确率高出28%</p>
                <p>• 建议避开疲惫时段处理待克服任务</p>
              </div>
            </div>

            {/* AI智能建议 */}
            <div className="bg-white rounded-xl shadow-sm p-3">
              <div className="flex justify-between items-center mb-2">
                <h2 className="font-medium text-sm">AI优化建议</h2>
                <button className="text-xs text-primary">更多</button>
              </div>
              <div className="text-xs text-gray-600 space-y-1.5">
                <p>• 可将"数学公式背诵"安排在19:00-20:00（你的记忆黄金时段）</p>
                <p>• 建议增加"撰写报告"的预备时间，历史完成时间比计划长30%</p>
                <p>• 周六安排1小时集中处理未完成的待克服任务</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <BottomNavBar />

      {/* 完整统计页面 */}
      {showFullStats && (
        <div className="fixed inset-0 bg-white z-50 overflow-y-auto">
          <div className="p-4 border-b border-gray-100 flex justify-between items-center sticky top-0 bg-white z-10">
            <h3 className="font-semibold">完整统计分析</h3>
            <button 
              onClick={() => setShowFullStats(false)}
              className="text-gray-500 p-1.5"
            >
              <i className="fa fa-times"></i>
            </button>
          </div>
          
          <div className="p-4 overflow-y-auto max-h-[calc(100vh-4rem)]">
            {/* 统计周期选择 */}
            <div className="flex gap-2 mb-6">
              <button className="bg-primary text-white px-3 py-1.5 rounded-full text-sm">本周</button>
              <button className="bg-gray-100 text-gray-500 px-3 py-1.5 rounded-full text-sm hover:bg-gray-200">本月</button>
              <button className="bg-gray-100 text-gray-500 px-3 py-1.5 rounded-full text-sm hover:bg-gray-200">全部</button>
            </div>
            
            {/* 详细图表 */}
            <div className="mb-6">
              <h4 className="font-medium text-sm mb-3">任务类别分布</h4>
              <div className="h-[220px] bg-gray-50 rounded-lg p-3">
                <Doughnut data={doughnutChartData} options={doughnutOptions} />
              </div>
            </div>
            
            {/* 高频任务统计 */}
            <div className="mb-6">
              <h4 className="font-medium text-sm mb-3">高频任务完成情况</h4>
              <div className="space-y-2">
                {[
                  { name: "英语阅读训练", completion: 100, hours: 3, focus: 85 },
                  { name: "整理资料", completion: 80, hours: 1.5, focus: 72 },
                  { name: "运动健身", completion: 60, hours: 2.5, focus: 88 }
                ].map((task, index) => (
                  <div key={index} className="bg-gray-50 rounded-lg p-3">
                    <div className="flex justify-between items-center mb-1">
                      <div className="flex items-center">
                        <span className="text-sm">{task.name}</span>
                        <span className="ml-2 inline-flex items-center justify-center w-4 h-4 bg-frequent text-white text-xs rounded-full">
                          <i className="fa fa-bolt"></i>
                        </span>
                      </div>
                      <div className="text-sm font-medium">{task.completion}%</div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div className="bg-frequent h-1.5 rounded-full" style={{width: `${task.completion}%`}}></div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      本周：{task.hours}小时 · 平均专注度：{task.focus}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* 待克服任务分析 */}
            <div>
              <h4 className="font-medium text-sm mb-3">待克服任务改进建议</h4>
              <div className="space-y-2">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center mb-2">
                    <span className="text-sm">数学公式背诵</span>
                    <span className="ml-2 inline-flex items-center justify-center w-4 h-4 bg-warning text-white text-xs rounded-full">
                      <i className="fa fa-exclamation"></i>
                    </span>
                  </div>
                  <div className="text-xs text-gray-600 space-y-1">
                    <p>• 完成率：50% · 平均耗时超出计划25%</p>
                    <p>• 建议：拆分任务为15分钟一段，使用间隔重复法</p>
                    <p>• 最佳完成时段：20:00-21:00（记忆效率高出平均18%）</p>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center mb-2">
                    <span className="text-sm">撰写报告</span>
                    <span className="ml-2 inline-flex items-center justify-center w-4 h-4 bg-warning text-white text-xs rounded-full">
                      <i className="fa fa-exclamation"></i>
                    </span>
                  </div>
                  <div className="text-xs text-gray-600 space-y-1">
                    <p>• 完成率：30% · 经常拖延至最后时刻</p>
                    <p>• 建议：先创建大纲，分章节完成，每完成一章奖励15分钟休息</p>
                    <p>• 最佳完成时段：14:00-16:00（创意指数最高）</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MainSchedulePage;
 