import React, { useState, useEffect } from 'react';
import UserTopNav from '../../components/Navbar/UserTopNav';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';
import './MainSchedulePage.css';
import scheduleService from '../../services/scheduleService';

// 导入子组件
import {
  QuickInputBar,
  TaskFilterTabs,
  TaskSearch,
  TaskList,
  TimeSlotList,
  WeeklyStatsOverview,
  WeeklyChart,
  AnalysisCards,
  FullStatsModal
} from './components';

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
      console.error('❌ 加载任务失败，使用示例数据:', error);
      // API失败时使用示例数据
      setTasks([
        {
          id: 1,
          name: '英语学习',
          type: 'study',
          category: '学习',
          weeklyHours: 14,
          isHighFrequency: true,
          isOvercome: false,
          expanded: false,
          subTasks: [
            { id: 11, name: '单词记忆', hours: 7, isHighFrequency: true, isOvercome: false },
            { id: 12, name: '阅读理解', hours: 5, isHighFrequency: false, isOvercome: false },
            { id: 13, name: '写作练习', hours: 2, isHighFrequency: false, isOvercome: true }
          ]
        },
        {
          id: 2,
          name: '数学学习',
          type: 'study',
          category: '学习',
          weeklyHours: 12,
          isHighFrequency: false,
          isOvercome: false,
          expanded: false,
          subTasks: [
            { id: 21, name: '高数刷题', hours: 6, isHighFrequency: false, isOvercome: false },
            { id: 22, name: '线代复习', hours: 4, isHighFrequency: false, isOvercome: false },
            { id: 23, name: '概率统计', hours: 2, isHighFrequency: false, isOvercome: true }
          ]
        },
        {
          id: 3,
          name: '专业课',
          type: 'study',
          category: '学习',
          weeklyHours: 10,
          isHighFrequency: false,
          isOvercome: false,
          expanded: false,
          subTasks: [
            { id: 31, name: '教材通读', hours: 5, isHighFrequency: false, isOvercome: false },
            { id: 32, name: '真题练习', hours: 3, isHighFrequency: false, isOvercome: false },
            { id: 33, name: '笔记整理', hours: 2, isHighFrequency: false, isOvercome: false }
          ]
        }
      ]);
    }
  };

  // 加载今日时间表
  const loadTimeSlots = async () => {
    try {
      const response = await scheduleService.getTodayTimeSlots(USER_ID);
      const apiSlots = response.time_slots || [];
      
      // 转换API数据格式
      const formattedSlots = apiSlots.map(slot => {
        // 构建显示名称：如果有子任务，显示"项目 - 子任务"，否则只显示项目名
        let displayName = '空闲时间';
        if (slot.task_name) {
          displayName = slot.task_name;
          if (slot.subtask_name) {
            displayName = `${slot.task_name} - ${slot.subtask_name}`;
          }
        }
        
        return {
          id: slot.id,
          time: slot.time_range,
          task: displayName,
          type: slot.task_type || 'life',
          category: slot.task_type || '空闲',
          status: slot.status,
          isHighFrequency: slot.is_high_frequency || false,
          isOvercome: slot.is_overcome || false,
          isAIRecommended: slot.is_ai_recommended,
          note: slot.note,
          aiTip: slot.ai_tip,
          mood: slot.mood
        };
      });
      
      setTimeSlots(formattedSlots);
      setScheduleOverview(response.overview);
      
      console.log('✅ 数据加载成功:', {
        任务数: formattedSlots.length,
        概览: response.overview
      });
    } catch (error) {
      console.error('❌ 加载时间表失败，使用示例数据:', error);
      // API失败时使用示例数据
      setTimeSlots([
        { id: 1, time: '06:00-07:00', task: '英语学习 - 单词记忆', type: 'study', category: '学习', status: 'completed', isHighFrequency: true, isOvercome: false, isAIRecommended: false },
        { id: 2, time: '07:00-08:00', task: '早餐+晨练', type: 'life', category: '生活', status: 'completed', isHighFrequency: false, isOvercome: false, isAIRecommended: false },
        { id: 3, time: '08:00-09:30', task: '数学学习 - 高数刷题', type: 'study', category: '学习', status: 'in_progress', isHighFrequency: false, isOvercome: false, isAIRecommended: true, aiTip: '建议先复习昨天错题，再做新题' },
        { id: 4, time: '09:30-10:00', task: '休息', type: 'rest', category: '休息', status: 'pending', isHighFrequency: false, isOvercome: false, isAIRecommended: false },
        { id: 5, time: '10:00-12:00', task: '专业课 - 教材通读', type: 'study', category: '学习', status: 'pending', isHighFrequency: false, isOvercome: false, isAIRecommended: false },
        { id: 6, time: '12:00-13:00', task: '午餐+午休', type: 'life', category: '生活', status: 'pending', isHighFrequency: false, isOvercome: false, isAIRecommended: false },
        { id: 7, time: '13:00-14:30', task: '英语学习 - 阅读理解', type: 'study', category: '学习', status: 'pending', isHighFrequency: false, isOvercome: false, isAIRecommended: false },
        { id: 8, time: '14:30-15:00', task: '休息', type: 'rest', category: '休息', status: 'pending', isHighFrequency: false, isOvercome: false, isAIRecommended: false },
        { id: 9, time: '15:00-17:00', task: '数学学习 - 线代复习', type: 'study', category: '学习', status: 'pending', isHighFrequency: false, isOvercome: false, isAIRecommended: false },
        { id: 10, time: '17:00-18:00', task: '晚餐+散步', type: 'life', category: '生活', status: 'pending', isHighFrequency: false, isOvercome: false, isAIRecommended: false },
        { id: 11, time: '18:00-19:30', task: '专业课 - 真题练习', type: 'study', category: '学习', status: 'pending', isHighFrequency: false, isOvercome: true, isAIRecommended: false },
        { id: 12, time: '19:30-20:00', task: '休息', type: 'rest', category: '休息', status: 'pending', isHighFrequency: false, isOvercome: false, isAIRecommended: false },
        { id: 13, time: '20:00-21:00', task: '英语学习 - 单词记忆', type: 'study', category: '学习', status: 'pending', isHighFrequency: true, isOvercome: false, isAIRecommended: false },
        { id: 14, time: '21:00-22:00', task: '复习总结', type: 'study', category: '学习', status: 'pending', isHighFrequency: false, isOvercome: false, isAIRecommended: false },
        { id: 15, time: '22:00-23:00', task: '洗漱+放松', type: 'life', category: '生活', status: 'pending', isHighFrequency: false, isOvercome: false, isAIRecommended: false }
      ]);
      setScheduleOverview({
        total_study_hours: 10.5,
        completed_slots: 2,
        total_slots: 15,
        completion_rate: 13.3,
        in_progress_slots: 1
      });
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
              <TaskFilterTabs
                activeFilter={activeFilter}
                onFilterClick={handleFilterClick}
              />

              {/* 任务搜索和筛选 */}
              <TaskSearch />

              {/* 任务列表 */}
              <TaskList
                tasks={tasks}
                activeFilter={activeFilter}
                expandedTasks={expandedTasks}
                onToggleTaskExpansion={toggleTaskExpansion}
              />
            </div>
          </div>

          {/* 右侧：时间表 */}
          <div className="lg:col-span-2">
            <TimeSlotList
              timeSlots={timeSlots}
              selectedMoods={selectedMoods}
              aiRecommendations={aiRecommendations}
              onMoodSelect={handleMoodSelect}
              onAiRecommendation={handleAiRecommendation}
            />
          </div>
        </div>

        {/* 快捷输入区 */}
        <QuickInputBar
          quickInput={quickInput}
          onQuickInputChange={setQuickInput}
          onQuickAdd={handleQuickAdd}
        />

        {/* 统计分析区 */}
        <div className="space-y-3 mb-20">
          {/* 本周统计概览 */}
          <WeeklyStatsOverview
            stats={stats}
            onShowFullStats={() => setShowFullStats(true)}
          />

          {/* 本周时间分布图表 */}
          <WeeklyChart
            chartData={weeklyChartData}
            chartOptions={chartOptions}
          />

          {/* 行为分析 */}
          <AnalysisCards />
        </div>
      </main>

      <BottomNavBar />

      {/* 完整统计页面 */}
      <FullStatsModal
        showFullStats={showFullStats}
        onClose={() => setShowFullStats(false)}
        doughnutChartData={doughnutChartData}
        doughnutOptions={doughnutOptions}
      />
    </div>
  );
};

export default MainSchedulePage;
 