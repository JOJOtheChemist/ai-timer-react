import React, { useState } from 'react';
import './TimeCalculatorPage.css';

const TimeCalculatorPage = () => {
  const [activeCategory, setActiveCategory] = useState('语言学习');
  const [selectedTarget, setSelectedTarget] = useState(0);
  const [dailyHours, setDailyHours] = useState('');
  const [weeklyDays, setWeeklyDays] = useState('6');
  const [currentLevel, setCurrentLevel] = useState('1.2');
  const [selectedSituations, setSelectedSituations] = useState(['失恋（情绪调节）']);
  const [result, setResult] = useState(null);
  const [showResult, setShowResult] = useState(false);

  const categories = ['语言学习', '技能考证', '升学考试', '职场提升'];

  const targetData = {
    '语言学习': [
      { name: '法语（A1-A2）', baseTime: 200, source: '126个案例均值' },
      { name: '英语（四级→六级）', baseTime: 180, source: '218个案例均值' },
      { name: '日语（N5-N3）', baseTime: 350, source: '97个案例均值' },
      { name: '韩语（TOPIK1-2）', baseTime: 220, source: '89个案例均值' }
    ],
    '技能考证': [
      { name: 'CPA（财务管理）', baseTime: 280, source: '156个案例均值' },
      { name: '教师资格证', baseTime: 120, source: '203个案例均值' },
      { name: 'PMP项目管理', baseTime: 150, source: '89个案例均值' },
      { name: '人力资源师', baseTime: 180, source: '134个案例均值' }
    ],
    '升学考试': [
      { name: '考研（英语一）', baseTime: 400, source: '298个案例均值' },
      { name: '考研（数学一）', baseTime: 450, source: '267个案例均值' },
      { name: '考研（政治）', baseTime: 200, source: '312个案例均值' },
      { name: '考公（行测+申论）', baseTime: 350, source: '189个案例均值' }
    ],
    '职场提升': [
      { name: 'Python编程', baseTime: 300, source: '145个案例均值' },
      { name: 'Excel高级技能', baseTime: 80, source: '203个案例均值' },
      { name: 'PPT设计提升', baseTime: 60, source: '167个案例均值' },
      { name: '数据分析师', baseTime: 250, source: '98个案例均值' }
    ]
  };

  const situations = [
    { name: '贫穷（需兼职）', coefficient: 0.30 },
    { name: '失恋（情绪调节）', coefficient: 0.20 },
    { name: '在职备考', coefficient: 0.40 },
    { name: '宝妈带娃', coefficient: 0.50 },
    { name: '熬夜拖延', coefficient: 0.25 },
    { name: '跨专业学习', coefficient: 0.35 }
  ];

  const recommendations = [
    {
      icon: '📚',
      title: '280小时法语A2上岸时间表',
      desc: '失恋期备考成功案例，可直接复用'
    },
    {
      icon: '🔄',
      title: '法语高效复习四步法',
      desc: '100+人打卡验证，提升30%效率'
    },
    {
      icon: '👩‍🏫',
      title: '法语认证导师1v1规划',
      desc: '针对0基础学员，定制专属计划'
    }
  ];

  const handleCategoryChange = (category) => {
    setActiveCategory(category);
    setSelectedTarget(0);
  };

  const handleTargetSelect = (index) => {
    setSelectedTarget(index);
  };

  const handleSituationToggle = (situationName) => {
    setSelectedSituations(prev => {
      if (prev.includes(situationName)) {
        return prev.filter(s => s !== situationName);
      } else {
        return [...prev, situationName];
      }
    });
  };

  const calculateTime = () => {
    if (!dailyHours || dailyHours <= 0) {
      alert('请输入有效的每日学习时长');
      return;
    }

    const currentTargets = targetData[activeCategory];
    const selectedTargetData = currentTargets[selectedTarget];
    const baseTime = selectedTargetData.baseTime;
    
    // 计算基础系数
    const levelCoefficient = parseFloat(currentLevel);
    
    // 计算特殊情况系数
    const situationCoefficient = selectedSituations.reduce((total, situationName) => {
      const situation = situations.find(s => s.name === situationName);
      return total + (situation ? situation.coefficient : 0);
    }, 0);
    
    // 总时长计算
    const totalHours = Math.round(baseTime * levelCoefficient * (1 + situationCoefficient));
    
    // 预计周期计算
    const weeklyHours = parseFloat(dailyHours) * parseInt(weeklyDays);
    const totalDays = Math.ceil(totalHours / parseFloat(dailyHours));
    
    // 生成测算依据说明
    const levelDesc = currentLevel === '1.2' ? '0基础(+20%)' : 
                     currentLevel === '1.0' ? '有基础(无额外)' : '进阶提升(-20%)';
    
    const situationDesc = selectedSituations.length > 0 ? 
      ` + ${selectedSituations.map(s => {
        const situation = situations.find(sit => sit.name === s);
        return s.split('（')[0] + `(+${Math.round(situation.coefficient * 100)}%)`;
      }).join(' + ')}` : '';

    const resultData = {
      totalHours,
      totalDays,
      dailyHours: parseFloat(dailyHours),
      weeklyDays: parseInt(weeklyDays),
      description: `测算依据：${selectedTargetData.name}基准${baseTime}h + ${levelDesc}${situationDesc}，按每日${dailyHours}h、每周${weeklyDays}天计算`
    };

    setResult(resultData);
    setShowResult(true);
  };

  const handleRecommendClick = (recommendation) => {
    alert(`查看推荐：${recommendation.title}`);
  };

  return (
    <div className="time-calculator-page">
      {/* 顶部导航栏 */}
      <div className="nav-top">
        <div className="back-btn" onClick={() => alert('返回上一页')}>←</div>
        <div className="title">时间计算器</div>
        <div className="home-btn" onClick={() => alert('回到首页')}>🏠</div>
      </div>

      {/* 页面容器 */}
      <div className="container">
        {/* 说明栏 */}
        <div className="intro-bar">
          <i>💡</i>
          <div>
            基于<span className="highlight">1000+真实上岸案例</span>测算基准时长，结合你的个人情况智能调整，结果更贴合实际！
          </div>
        </div>

        {/* 目标选择区 */}
        <div className="section-title">选择你的目标</div>
        <div className="target-categories">
          {/* 分类标签 */}
          <div className="category-tab">
            {categories.map(category => (
              <button 
                key={category}
                className={`tab-btn ${activeCategory === category ? 'active' : ''}`}
                onClick={() => handleCategoryChange(category)}
              >
                {category}
              </button>
            ))}
          </div>

          {/* 目标列表 */}
          <div className="target-list">
            {targetData[activeCategory].map((target, index) => (
              <div 
                key={index}
                className={`target-card ${selectedTarget === index ? 'active' : ''}`}
                onClick={() => handleTargetSelect(index)}
              >
                <div className="target-name">{target.name}</div>
                <div className="base-time">基准时长：{target.baseTime}小时</div>
                <div className="source">{target.source}</div>
              </div>
            ))}
          </div>
        </div>

        {/* 个性化测算区 */}
        <div className="section-title">你的个人情况</div>
        <div className="calculator-form">
          {/* 每日可投入时长 */}
          <div className="form-group">
            <label className="form-label">每日可投入时长（小时）</label>
            <input 
              type="number" 
              className="form-input" 
              placeholder="例如：2" 
              min="0.5" 
              max="16" 
              step="0.5"
              value={dailyHours}
              onChange={(e) => setDailyHours(e.target.value)}
            />
            <div className="input-note">建议填写真实可坚持的时长，避免过度规划</div>
          </div>

          {/* 每周投入天数 */}
          <div className="form-group">
            <label className="form-label">每周投入天数</label>
            <select 
              className="select-group"
              value={weeklyDays}
              onChange={(e) => setWeeklyDays(e.target.value)}
            >
              <option value="7">7天（全勤）</option>
              <option value="6">6天（休息1天）</option>
              <option value="5">5天（工作日学习）</option>
              <option value="4">4天（灵活安排）</option>
            </select>
          </div>

          {/* 当前基础 */}
          <div className="form-group">
            <label className="form-label">当前基础</label>
            <select 
              className="select-group"
              value={currentLevel}
              onChange={(e) => setCurrentLevel(e.target.value)}
            >
              <option value="1.2">0基础（需额外20%时长）</option>
              <option value="1.0">有基础（无需额外时长）</option>
              <option value="0.8">进阶提升（减少20%时长）</option>
            </select>
          </div>

          {/* 特殊情况（时间膨胀） */}
          <div className="form-group">
            <label className="form-label">特殊情况（可多选，影响时长）</label>
            <div className="situation-tags">
              {situations.map(situation => (
                <div 
                  key={situation.name}
                  className={`situation-tag ${selectedSituations.includes(situation.name) ? 'active' : ''}`}
                  onClick={() => handleSituationToggle(situation.name)}
                >
                  {situation.name}
                  <span className="coefficient">+{Math.round(situation.coefficient * 100)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 计算按钮 */}
        <button className="calc-btn" onClick={calculateTime}>开始测算</button>

        {/* 结果展示区 */}
        {showResult && result && (
          <div className="result-area show">
            <div className="result-title">你的个性化时间规划</div>
            <div className="result-cards">
              <div className="result-card">
                <div className="result-label">理论总时长</div>
                <div className="result-value">{result.totalHours}h</div>
              </div>
              <div className="result-card">
                <div className="result-label">预计周期</div>
                <div className="result-value">{result.totalDays}天</div>
              </div>
              <div className="result-card">
                <div className="result-label">每日建议</div>
                <div className="result-value">{result.dailyHours}h</div>
              </div>
            </div>
            <div className="result-desc">
              {result.description}
            </div>
          </div>
        )}

        {/* 推荐区 */}
        <div className="section-title">为你推荐</div>
        <div className="recommend-area">
          <div className="recommend-list">
            {recommendations.map((recommendation, index) => (
              <div 
                key={index}
                className="recommend-card" 
                onClick={() => handleRecommendClick(recommendation)}
              >
                <div className="recommend-icon">{recommendation.icon}</div>
                <div className="recommend-info">
                  <div className="recommend-title">{recommendation.title}</div>
                  <div className="recommend-desc">{recommendation.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 底部提示 */}
      <div className="bottom-tip">
        上传你的上岸时间表，赢<span>品牌高奢真皮包</span> | 测算结果仅供参考，可灵活调整
      </div>
    </div>
  );
};

export default TimeCalculatorPage; 