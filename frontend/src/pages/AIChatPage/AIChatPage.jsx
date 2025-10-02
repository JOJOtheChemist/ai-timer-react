import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import {
  ChatTopNav,
  ChatMessageItem,
  ChatToolBar,
  ChatInputArea,
  JumpModal
} from './components';
import './AIChatPage.css';

const AIChatPage = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [showJumpModal, setShowJumpModal] = useState(false);
  const [modalConfig, setModalConfig] = useState({});
  const [isMinimized, setIsMinimized] = useState(false);
  const chatAreaRef = useRef(null);

  // 初始消息
  const initialMessages = [
    {
      id: 1,
      type: 'ai',
      avatar: '🤖',
      content: '你好！我已分析完你近7天的时间表，发现了一些可以优化的地方，帮你整理了关键问题和推荐内容~',
      time: '09:25',
      timestamp: Date.now() - 300000
    },
    {
      id: 2,
      type: 'ai',
      avatar: '🤖',
      content: '',
      time: '09:26',
      timestamp: Date.now() - 240000,
      isAnalysis: true,
      analysisData: {
        tags: ['复习不足', '时间碎片化', '英语投入失衡'],
        analysis: '具体分析：近7天仅复习2次，且集中在深夜效率低；英语阅读每天投入2.5h，远超合理占比（建议1.5h），挤压了专业课时间。',
        recommendations: [
          {
            type: 'method',
            icon: '📚',
            name: '艾宾浩斯复习四步法',
            desc: '针对复习不足问题，按周期自动提醒复盘，已帮助300+人提升记忆效率',
            tag: '去打卡',
            path: '/study-method'
          },
          {
            type: 'case',
            icon: '🎯',
            name: '2100小时考研英语提分案例',
            desc: '同款"复习薄弱+英语失衡"问题，调整时间分配后英语从58分提至76分',
            tag: '看详情',
            path: '/success'
          },
          {
            type: 'tutor',
            icon: '⭐',
            name: '王英语老师（认证导师）',
            desc: '擅长考研英语时间规划，98%好评，已指导126人上岸',
            tag: '找TA指导',
            path: '/tutor'
          }
        ]
      }
    },
    {
      id: 3,
      type: 'user',
      avatar: '👩',
      content: '那这个艾宾浩斯复习法具体怎么用呀？和我的时间表怎么结合呢？',
      time: '09:28',
      timestamp: Date.now() - 120000
    },
    {
      id: 4,
      type: 'ai',
      avatar: '🤖',
      content: '很棒的问题！艾宾浩斯复习法可直接嵌入你的时间表：\n1. 早上7:00-7:30：复习前一天的英语单词和专业课笔记（对应新学内容12h后复盘）；\n2. 晚上20:00-20:20：复习当天所有内容（对应新学内容4-6h后复盘）；\n3. 每周六上午：复习本周重点（周复盘）。',
      time: '09:29',
      timestamp: Date.now() - 60000,
      hasRecommendation: true,
      recommendation: {
        type: 'method',
        icon: '📚',
        name: '艾宾浩斯复习法详情',
        desc: '点击查看完整周期表+打卡模板，可直接同步到你的时间表',
        tag: '立即同步',
        path: '/study-method'
      }
    }
  ];

  // 工具按钮配置
  const toolButtons = [
    { icon: '📊', text: '复盘总结', action: 'summary' },
    { icon: '👩‍🏫', text: '找导师', action: 'tutor', path: '/tutor' },
    { icon: '📅', text: '生成计划', action: 'plan' },
    { icon: '🔍', text: '查案例', action: 'cases', path: '/success' },
    { icon: '💡', text: '学习方法', action: 'methods', path: '/study-method' },
    { icon: '📝', text: '历史记录', action: 'history' }
  ];

  // 跳转弹窗配置
  const jumpModalConfigs = {
    method: {
      icon: '📚',
      title: '前往学习方法页',
      desc: '查看完整的学习方法教程、打卡模板及用户评价'
    },
    case: {
      icon: '🎯',
      title: '前往上岸时间表页',
      desc: '查看相似案例的完整时间记录和上岸经验分享'
    },
    tutor: {
      icon: '👩‍🏫',
      title: '前往导师详情页',
      desc: '查看导师资质、服务内容及学员真实评价'
    }
  };

  // 初始化消息
  useEffect(() => {
    setMessages(initialMessages);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // 发送消息
  const handleSendMessage = () => {
    const text = inputValue.trim();
    if (!text) return;

    const newMessage = {
      id: Date.now(),
      type: 'user',
      avatar: '👩',
      content: text,
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, newMessage]);
    setInputValue('');

    // 模拟AI回复
    setTimeout(() => {
      const aiReply = {
        id: Date.now() + 1,
        type: 'ai',
        avatar: '🤖',
        content: `已收到你的问题："${text}"，正在为你分析并整理答案...`,
        time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, aiReply]);
    }, 1000);
  };

  // 处理推荐卡片点击
  const handleRecommendClick = (recommendation) => {
    const config = jumpModalConfigs[recommendation.type];
    if (config) {
      setModalConfig({
        ...config,
        desc: `「${recommendation.name}」${config.desc}`,
        path: recommendation.path
      });
      setShowJumpModal(true);
    }
  };

  // 处理工具按钮点击
  const handleToolClick = (tool) => {
    if (tool.path) {
      navigate(tool.path);
    } else {
      alert(`触发「${tool.text}」功能（实际开发中调用对应工具）`);
    }
  };

  // 确认跳转
  const handleConfirmJump = () => {
    if (modalConfig.path) {
      navigate(modalConfig.path);
    }
    setShowJumpModal(false);
  };

  // 处理键盘事件
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  // 最小化功能
  const handleMinimize = () => {
    setIsMinimized(true);
    alert('AI对话区已最小化（实际开发中切换至主页面底部缩略态）');
  };

  // 返回功能
  const handleBack = () => {
    navigate(-1);
  };

  return (
    <div className={`ai-chat-page ${isMinimized ? 'minimized' : ''}`}>
      {/* 顶部导航栏 */}
      <ChatTopNav 
        onBack={handleBack}
        onMinimize={handleMinimize}
      />

      {/* 页面容器 */}
      <div className="container">
        {/* AI对话区 */}
        <div className="chat-area" ref={chatAreaRef}>
          {messages.map(message => (
            <ChatMessageItem
              key={message.id}
              message={message}
              onRecommendClick={handleRecommendClick}
            />
          ))}
        </div>

        {/* 功能工具条 */}
        <ChatToolBar
          tools={toolButtons}
          onToolClick={handleToolClick}
        />

        {/* 输入区 */}
        <ChatInputArea
          inputValue={inputValue}
          onInputChange={setInputValue}
          onSend={handleSendMessage}
          onKeyDown={handleKeyDown}
        />
      </div>

      {/* 跳转提示弹窗 */}
      <JumpModal
        isOpen={showJumpModal}
        modalConfig={modalConfig}
        onConfirm={handleConfirmJump}
        onCancel={() => setShowJumpModal(false)}
      />

      <BottomNavBar />
    </div>
  );
};

export default AIChatPage; 