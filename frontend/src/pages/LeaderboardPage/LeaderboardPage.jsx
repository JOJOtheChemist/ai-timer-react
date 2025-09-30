import React, { useState } from 'react';
import './LeaderboardPage.css';

const LeaderboardPage = () => {
  const [activeTab, setActiveTab] = useState('ranking');
  const [activeRanking, setActiveRanking] = useState('周记录时长榜');
  
  const rankingTypes = ['周记录时长榜', '月记录时长榜', '学习方法打卡榜', '上岸案例贡献榜'];
  
  const rankings = [
    { id: 1, name: 'CPA备考中', avatar: '👩‍💼', score: '235h', rank: 1, desc: '目标：通过CPA' },
    { id: 2, name: '考研的小琳', avatar: '👩‍🎓', score: '210h', rank: 2, desc: '目标：上岸985' },
    { id: 3, name: '学Python的阿美', avatar: '👩‍💻', score: '198h', rank: 3, desc: '目标：转行程序员' },
    { id: 4, name: '法语入门', avatar: '📚', score: '186h', rank: 4, desc: '目标：3个月达A2' },
    { id: 5, name: '设计考研菌', avatar: '🎨', score: '172h', rank: 5, desc: '目标：上岸美院' },
    { id: 6, name: '考公的小楠', avatar: '📝', score: '165h', rank: 6, desc: '目标：国考上岸' },
    { id: 7, name: '在职学英语', avatar: '💡', score: '158h', rank: 7, desc: '目标：雅思7.0' }
  ];

  const prizes = [
    {
      id: 1,
      name: '品牌定制胸衣包',
      desc: '头层牛皮，百搭通勤款',
      icon: '👜',
      tag: '热门'
    },
    {
      id: 2,
      name: '珍珠镶嵌首饰套装',
      desc: '银镀金材质，精致百搭',
      icon: '💍'
    },
    {
      id: 3,
      name: '真皮复古头饰',
      desc: '手工缝制，质感高级',
      icon: '👒'
    },
    {
      id: 4,
      name: '迷你真皮零钱包',
      desc: '便携设计，多色可选',
      icon: '👛'
    }
  ];

  const winners = ['琳', '美', '楠', '婷', '琪', '...'];

  const rules = [
    '1. 需上传完整上岸时间表（含每日任务+时长记录，持续时间≥30天）及上岸证明（录取通知书/证书/入职offer等）；',
    '2. 数据需真实有效，平台将进行人工审核，虚假数据将取消资格；',
    '3. 入选案例将展示在"上岸时间表"板块，标注上传者昵称（可匿名）；',
    '4. 每月评选10名优质案例获得者，随机发放奖品，快递包邮；',
    '5. 上传即视为同意平台将数据用于案例展示及优化AI测算模型。'
  ];

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  const handleRankingTypeChange = (type) => {
    setActiveRanking(type);
  };

  const handleAdUpload = () => {
    alert('即将跳转至"我的时间表"选择上传内容');
  };

  const handlePrizeClick = (prize) => {
    alert(`查看${prize.name}详情（实际开发中为图片放大预览）`);
  };

  const myRankData = {
    avatar: '👩',
    name: '你的昵称',
    desc: '当前周榜排名：第156名',
    score: '128h'
  };

  return (
    <div className="leaderboard-page">
      {/* 顶部导航栏 */}
      <div className="nav-top">
        <div className="back-btn" onClick={() => alert('返回上一页')}>←</div>
        <div className="title">激励中心</div>
        <div className="home-btn" onClick={() => alert('回到首页')}>🏠</div>
      </div>

      {/* 页面容器 */}
      <div className="container">
        {/* 子页面切换标签 */}
        <div className="tab-container">
          <button 
            className={`tab-btn ${activeTab === 'ranking' ? 'active' : ''}`}
            onClick={() => handleTabChange('ranking')}
          >
            排行榜
          </button>
          <button 
            className={`tab-btn ${activeTab === 'ad' ? 'active' : ''}`}
            onClick={() => handleTabChange('ad')}
          >
            广告征集
          </button>
        </div>

        {/* 排行榜页面 */}
        {activeTab === 'ranking' && (
          <div className="ranking-page">
            {/* 榜单类型切换 */}
            <div className="ranking-tab">
              {rankingTypes.map(type => (
                <div 
                  key={type}
                  className={`ranking-type ${activeRanking === type ? 'active' : ''}`}
                  onClick={() => handleRankingTypeChange(type)}
                >
                  {type}
                </div>
              ))}
            </div>

            {/* 我的排名 */}
            <div className="my-rank">
              <div className="my-avatar">{myRankData.avatar}</div>
              <div className="my-info">
                <div className="my-name">{myRankData.name}</div>
                <div className="my-rank-desc">{myRankData.desc}</div>
              </div>
              <div className="my-score">{myRankData.score}</div>
            </div>

            {/* 前三名展示 */}
            <div className="top3-ranking">
              {/* 第二名（突出显示） */}
              <div className="top-ranker">
                <div className="rank-medal medal-2">2</div>
                <div className="top-avatar">{rankings[1].avatar}</div>
                <div className="top-name">{rankings[1].name}</div>
                <div className="top-score">{rankings[1].score}</div>
              </div>
              {/* 第一名 */}
              <div className="top-ranker">
                <div className="rank-medal medal-1">1</div>
                <div className="top-avatar">{rankings[0].avatar}</div>
                <div className="top-name">{rankings[0].name}</div>
                <div className="top-score">{rankings[0].score}</div>
              </div>
              {/* 第三名 */}
              <div className="top-ranker">
                <div className="rank-medal medal-3">3</div>
                <div className="top-avatar">{rankings[2].avatar}</div>
                <div className="top-name">{rankings[2].name}</div>
                <div className="top-score">{rankings[2].score}</div>
              </div>
            </div>

            {/* 榜单列表 */}
            <div className="ranking-list">
              {rankings.slice(3).map(user => (
                <div key={user.id} className="ranker-item">
                  <div className="rank-number">{user.rank}</div>
                  <div className="rank-avatar">{user.avatar}</div>
                  <div className="rank-info">
                    <div className="rank-name">{user.name}</div>
                    <div className="rank-desc">{user.desc}</div>
                  </div>
                  <div className="rank-score">{user.score}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 广告征集页面 */}
        {activeTab === 'ad' && (
          <div className="ad-page active">
            {/* 广告头部banner */}
            <div className="ad-banner">
              <div className="ad-title">上传上岸时间表，赢高奢真皮包</div>
              <div className="ad-subtitle">真实案例可获品牌定制首饰/包包，女性专属福利！</div>
              <button className="ad-btn" onClick={handleAdUpload}>立即上传时间表</button>
            </div>

            {/* 奖品展示区 */}
            <div className="prize-section">
              <div className="section-title">专属奖品池</div>
              <div className="prize-list">
                {prizes.map(prize => (
                  <div key={prize.id} className="prize-card" onClick={() => handlePrizeClick(prize)}>
                    <div className="prize-img">
                      {prize.icon}
                      {prize.tag && <span className="prize-tag">{prize.tag}</span>}
                    </div>
                    <div className="prize-info">
                      <div className="prize-name">{prize.name}</div>
                      <div className="prize-desc">{prize.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 规则说明区 */}
            <div className="rule-section">
              <div className="section-title">参与规则</div>
              <ul className="rule-list">
                {rules.map((rule, index) => (
                  <li key={index} className="rule-item">
                    {rule.split('完整上岸时间表').map((part, i) => 
                      i === 0 ? part : [<span key={i} className="highlight">完整上岸时间表</span>, ...part.split('上岸证明').map((subpart, j) => 
                        j === 0 ? subpart : [<span key={j} className="highlight">上岸证明</span>, subpart]
                      )]
                    )}
                  </li>
                ))}
              </ul>
            </div>

            {/* 已入选名单 */}
            <div className="winner-section">
              <div className="section-title">本月已入选用户</div>
              <div className="winner-list">
                {winners.map((winner, index) => (
                  <div key={index} className="winner-avatar">{winner}</div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 底部提示 */}
      <div className="bottom-tip">
        记录时间=积累成长=赢取好礼 | <span>每周一0点更新排行榜</span>
      </div>
    </div>
  );
};

export default LeaderboardPage; 