import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './MomentsPage.css';

const MomentsPage = () => {
  const navigate = useNavigate();
  const [activeMode, setActiveMode] = useState('dynamic'); // 'dynamic' or 'dryGoods'
  const [searchQuery, setSearchQuery] = useState('');
  const [showPostModal, setShowPostModal] = useState(false);
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [postMode, setPostMode] = useState('dynamic');
  const [selectedTags, setSelectedTags] = useState(['全部标签']);
  const [selectedTime, setSelectedTime] = useState(['全部时间']);
  const [selectedHot, setSelectedHot] = useState(['推荐']);

  // 动态内容数据
  const dynamicPosts = [
    {
      id: 1,
      type: 'ad',
      user: { name: '平台活动', avatar: '🏆' },
      time: '置顶',
      title: '上传上岸时间表，赢高奢真皮包！',
      content: '真实时间表+上岸证明=品牌定制包，已有28人获奖，点击参与→',
      tags: ['#上传时间表', '#赢奖品'],
      stats: { likes: 0, comments: 0, shares: 0 },
      isAd: true,
      adInfo: '奖品：真皮笔记本/珍珠首饰'
    },
    {
      id: 2,
      user: { name: '考研的小琳', avatar: '琳' },
      time: '10分钟前',
      content: '今天做英语阅读错了5道😩 #考研英语 #今日复盘 感觉长难句还是没吃透...',
      tags: ['#考研英语', '#今日复盘'],
      stats: { likes: 12, comments: 3, shares: 0 }
    },
    {
      id: 3,
      user: { name: '琪琪要上岸', avatar: '琪' },
      time: '1小时前',
      content: '图书馆学习氛围太好了！专注了4小时💪 #图书馆打卡 推荐大家试试番茄工作法，真的有用！',
      tags: ['#图书馆打卡'],
      stats: { likes: 36, comments: 12, shares: 0 },
      image: 'https://picsum.photos/400/240?random=1'
    }
  ];

  // 干货内容数据
  const dryGoodsPosts = [
    {
      id: 4,
      user: { name: '考研的小艾', avatar: '艾' },
      time: '昨天 19:45',
      title: '考研英语3个月提分18分的时间表模板',
      content: '每天1.5h精读+1h单词，用 @艾宾浩斯复习法 复盘，感谢 @王英语老师 的规划！',
      tags: ['#考研英语', '#时间表模板', '#提分经验'],
      stats: { likes: 156, comments: 42, shares: 28 },
      image: 'https://picsum.photos/400/240?random=2',
      attachments: [
        { icon: 'fa-calendar-o', text: '关联时间表：7.15-7.21（186h）' },
        { icon: 'fa-paperclip', text: '附件：英语时间表.xlsx' }
      ]
    },
    {
      id: 5,
      user: { name: '张学姐笔记', avatar: '张' },
      time: '3天前',
      title: '财务管理高频考点整理（附记忆方法）',
      content: '整理了近5年财务管理考研高频考点，特别是 #长期股权投资 这一章，结合 @思维导图学习法 记忆效率翻倍！',
      tags: ['#财务管理', '#考点整理', '#记忆方法'],
      stats: { likes: 215, comments: 58, shares: 42 },
      attachments: [
        { icon: 'fa-calendar-o', text: '关联学习计划：第8周' },
        { icon: 'fa-bar-chart', text: '正确率提升：65%→82%' }
      ]
    }
  ];

  // 情绪标签
  const moodTags = ['#效率低😩', '#进度快💪', '#有疑问❓', '#很开心😊', '#求鼓励💖'];

  // 筛选标签
  const filterTags = ['#全部标签', '#考研英语', '#财务管理', '#时间表', '#记忆方法', '#学习经验', '#图书馆', '#每日复盘'];
  const timeFilters = ['全部时间', '今天', '本周', '本月'];
  const hotFilters = ['推荐', '最新', '最热'];

  // 处理模式切换
  const handleModeSwitch = (mode) => {
    setActiveMode(mode);
  };

  // 处理搜索
  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      console.log('搜索:', searchQuery);
    }
  };

  // 处理点赞
  const handleLike = (postId, isLiked) => {
    console.log(`${isLiked ? '取消点赞' : '点赞'} 帖子 ${postId}`);
  };

  // 处理评论
  const handleComment = (postId) => {
    console.log('查看评论区', postId);
  };

  // 处理分享
  const handleShare = (postId) => {
    console.log('分享内容', postId);
  };

  // 处理收藏
  const handleBookmark = (postId, isBookmarked) => {
    console.log(`${isBookmarked ? '取消收藏' : '收藏'} 帖子 ${postId}`);
  };

  // 处理发布
  const handlePost = (content, tags) => {
    console.log('发布内容:', { content, tags, mode: postMode });
    setShowPostModal(false);
  };

  // 处理筛选
  const handleFilter = () => {
    console.log('筛选条件:', { selectedTags, selectedTime, selectedHot });
    setShowFilterModal(false);
  };

  // 处理标签选择
  const handleTagSelect = (tag, type) => {
    if (type === 'tags') {
      if (tag === '#全部标签') {
        setSelectedTags(['全部标签']);
      } else {
        const newTags = selectedTags.includes('全部标签') 
          ? [tag] 
          : selectedTags.includes(tag)
            ? selectedTags.filter(t => t !== tag)
            : [...selectedTags.filter(t => t !== '全部标签'), tag];
        setSelectedTags(newTags.length === 0 ? ['全部标签'] : newTags);
      }
    } else if (type === 'time') {
      setSelectedTime([tag]);
    } else if (type === 'hot') {
      setSelectedHot([tag]);
    }
  };

  // 渲染帖子卡片
  const renderPostCard = (post) => (
    <div key={post.id} className={`post-card ${post.isAd ? 'ad-card' : ''}`}>
      {post.isAd && (
        <div className="ad-header">
          <span className="ad-badge">
            <i className="fa fa-bullhorn"></i>推荐
          </span>
          <div className="ad-pin">置顶</div>
        </div>
      )}
      
      <div className="post-user">
        <div className="user-avatar">{post.user.avatar}</div>
        <div className="user-info">
          <div className="user-name">{post.user.name}</div>
          <div className="post-time">{post.time}</div>
        </div>
      </div>

      {post.title && <h3 className="post-title">{post.title}</h3>}
      
      <div className="post-content">
        {post.content}
      </div>

      {post.adInfo && (
        <div className="ad-info">
          <i className="fa fa-gift"></i> {post.adInfo}
        </div>
      )}

      {post.attachments && (
        <div className="post-attachments">
          {post.attachments.map((attachment, index) => (
            <div key={index} className="attachment-item">
              <i className={`fa ${attachment.icon}`}></i>
              {attachment.text}
            </div>
          ))}
        </div>
      )}

      {post.image && (
        <div className="post-image">
          <img src={post.image} alt="帖子图片" />
        </div>
      )}

      <div className="post-tags">
        {post.tags.map((tag, index) => (
          <span key={index} className="tag">{tag}</span>
        ))}
      </div>

      <div className="post-actions">
        <div className="action-buttons">
          <button className="action-btn like-btn" onClick={() => handleLike(post.id, false)}>
            <i className="fa fa-heart-o"></i> {post.stats.likes}
          </button>
          <button className="action-btn comment-btn" onClick={() => handleComment(post.id)}>
            <i className="fa fa-comment-o"></i> {post.stats.comments}
          </button>
          <button className="action-btn share-btn" onClick={() => handleShare(post.id)}>
            <i className="fa fa-share"></i> {post.stats.shares > 0 ? post.stats.shares : '转发'}
          </button>
        </div>
        {!post.isAd && (
          <button className="bookmark-btn" onClick={() => handleBookmark(post.id, false)}>
            <i className="fa fa-bookmark-o"></i> 收藏
          </button>
        )}
      </div>
    </div>
  );

  return (
    <div className="moments-page">
      {/* 顶部导航栏 */}
      <header className="top-nav">
        <button className="back-btn" onClick={() => navigate(-1)}>
          <i className="fa fa-angle-left"></i>
        </button>
        <h1>动态广场</h1>
        <button className="filter-btn" onClick={() => setShowFilterModal(true)}>
          <i className="fa fa-filter"></i>
        </button>
      </header>

      {/* 主内容区 */}
      <main className="main-content">
        {/* 搜索栏 */}
        <div className="search-bar">
          <i className="fa fa-search search-icon"></i>
          <input 
            type="text" 
            placeholder="搜索标签/内容/用户"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleSearch}
          />
        </div>

        {/* 模式切换区 */}
        <div className="mode-switch">
          <button 
            className={`mode-btn ${activeMode === 'dynamic' ? 'active' : ''}`}
            onClick={() => handleModeSwitch('dynamic')}
          >
            动态
          </button>
          <button 
            className={`mode-btn ${activeMode === 'dryGoods' ? 'active' : ''}`}
            onClick={() => handleModeSwitch('dryGoods')}
          >
            干货
          </button>
        </div>

        {/* 内容展示区 */}
        <div className="content-area">
          {activeMode === 'dynamic' 
            ? dynamicPosts.map(renderPostCard)
            : dryGoodsPosts.map(renderPostCard)
          }
        </div>

        {/* 加载更多 */}
        <div className="load-more">
          <button className="load-more-btn">
            加载更多
            <i className="fa fa-angle-down"></i>
          </button>
        </div>
      </main>

      {/* 发布按钮 */}
      <button className="floating-post-btn" onClick={() => setShowPostModal(true)}>
        <i className="fa fa-plus"></i>
      </button>

      {/* 发布面板模态框 */}
      {showPostModal && (
        <div className="modal-overlay" onClick={() => setShowPostModal(false)}>
          <div className="post-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>发布内容</h3>
              <button onClick={() => setShowPostModal(false)}>
                <i className="fa fa-times"></i>
              </button>
            </div>

            <div className="post-mode-switch">
              <button 
                className={`post-mode-btn ${postMode === 'dynamic' ? 'active' : ''}`}
                onClick={() => setPostMode('dynamic')}
              >
                动态
              </button>
              <button 
                className={`post-mode-btn ${postMode === 'dryGoods' ? 'active' : ''}`}
                onClick={() => setPostMode('dryGoods')}
              >
                干货
              </button>
            </div>

            {postMode === 'dynamic' ? (
              <div className="dynamic-post-area">
                <textarea placeholder="分享你的学习状态和感悟..."></textarea>
                <div className="mood-tags">
                  <p>添加情绪标签</p>
                  <div className="tag-list">
                    {moodTags.map((tag, index) => (
                      <span key={index} className="mood-tag">{tag}</span>
                    ))}
                  </div>
                </div>
                <div className="post-tools">
                  <div className="tool-buttons">
                    <button><i className="fa fa-image"></i></button>
                    <button><i className="fa fa-smile-o"></i></button>
                    <button><i className="fa fa-tag"></i></button>
                  </div>
                  <button className="publish-btn">发布</button>
                </div>
              </div>
            ) : (
              <div className="drygoods-post-area">
                <input type="text" placeholder="给你的干货起个标题吧..." />
                <textarea placeholder="分享你的学习经验、方法或资料..."></textarea>
                <div className="relation-content">
                  <p>关联内容</p>
                  <div className="relation-buttons">
                    <button><i className="fa fa-calendar-o"></i> 我的时间表</button>
                    <button><i className="fa fa-lightbulb-o"></i> 学习方法</button>
                    <button><i className="fa fa-user-o"></i> 导师</button>
                  </div>
                </div>
                <div className="content-tags">
                  <p>添加标签</p>
                  <div className="tag-list">
                    {['#考研英语', '#时间表模板', '#记忆方法', '#财务管理', '#考点整理'].map((tag, index) => (
                      <span key={index} className="content-tag">{tag}</span>
                    ))}
                  </div>
                </div>
                <div className="post-tools">
                  <div className="tool-buttons">
                    <button><i className="fa fa-image"></i></button>
                    <button><i className="fa fa-file-o"></i></button>
                    <button><i className="fa fa-tag"></i></button>
                  </div>
                  <button className="publish-btn">发布</button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 筛选面板模态框 */}
      {showFilterModal && (
        <div className="modal-overlay" onClick={() => setShowFilterModal(false)}>
          <div className="filter-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>筛选内容</h3>
              <button onClick={() => setShowFilterModal(false)}>
                <i className="fa fa-times"></i>
              </button>
            </div>

            <div className="filter-section">
              <p>按标签筛选</p>
              <div className="filter-tags">
                {filterTags.map((tag, index) => (
                  <span 
                    key={index}
                    className={`filter-tag ${selectedTags.includes(tag) ? 'active' : ''}`}
                    onClick={() => handleTagSelect(tag, 'tags')}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div className="filter-section">
              <p>按时间筛选</p>
              <div className="filter-tags">
                {timeFilters.map((time, index) => (
                  <span 
                    key={index}
                    className={`filter-tag ${selectedTime.includes(time) ? 'active' : ''}`}
                    onClick={() => handleTagSelect(time, 'time')}
                  >
                    {time}
                  </span>
                ))}
              </div>
            </div>

            <div className="filter-section">
              <p>按热度筛选</p>
              <div className="filter-tags">
                {hotFilters.map((hot, index) => (
                  <span 
                    key={index}
                    className={`filter-tag ${selectedHot.includes(hot) ? 'active' : ''}`}
                    onClick={() => handleTagSelect(hot, 'hot')}
                  >
                    {hot}
                  </span>
                ))}
              </div>
            </div>

            <button className="confirm-filter-btn" onClick={handleFilter}>
              确认筛选
            </button>
          </div>
        </div>
      )}

      <BottomNavBar />
    </div>
  );
};

export default MomentsPage;
