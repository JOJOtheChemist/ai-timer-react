import api from './api';

// ==================== 动态列表 API ====================

/**
 * 获取动态列表
 * @param {Object} params - 查询参数
 * @param {string} params.moment_type - 类型：dynamic/dryGoods
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {Array<string>} params.tags - 标签筛选
 * @param {string} params.time_range - 时间范围：today/week/month/all
 * @param {string} params.hot_type - 热度排序
 * @returns {Promise}
 */
export const getMomentList = async (params = {}) => {
  try {
    const queryParams = new URLSearchParams();
    
    // user_id 用于身份验证（判断点赞状态等）
    const userId = params.user_id || 1;
    queryParams.append('user_id', userId);
    
    // 类型参数（dynamic/dryGoods）
    if (params.moment_type) {
      queryParams.append('moment_type', params.moment_type);
    }
    
    // 分页参数
    if (params.page) {
      queryParams.append('page', params.page);
    }
    if (params.page_size) {
      queryParams.append('page_size', params.page_size);
    }
    
    // 筛选参数
    if (params.tags && params.tags.length > 0) {
      params.tags.forEach(tag => queryParams.append('tags', tag));
    }
    if (params.time_range) {
      queryParams.append('time_range', params.time_range);
    }
    if (params.hot_type) {
      queryParams.append('hot_type', params.hot_type);
    }
    
    const queryString = queryParams.toString();
    const url = `/v1/moments?${queryString}`;
    
    const response = await api.get(url);
    return response;
  } catch (error) {
    console.error('获取动态列表失败:', error);
    throw error;
  }
};

/**
 * 搜索动态
 * @param {string} keyword - 搜索关键词
 * @param {number} page - 页码
 * @param {number} page_size - 每页数量
 * @returns {Promise}
 */
export const searchMoments = async (keyword, page = 1, page_size = 10) => {
  try {
    const queryParams = new URLSearchParams({
      keyword,
      page,
      page_size,
      user_id: 1
    });
    
    const response = await api.get(`/v1/moments/search?${queryParams.toString()}`);
    return response;
  } catch (error) {
    console.error('搜索动态失败:', error);
    throw error;
  }
};

/**
 * 获取热门标签
 * @param {string} moment_type - 类型：dynamic/dryGoods
 * @returns {Promise}
 */
export const getPopularTags = async (moment_type = 'dynamic') => {
  try {
    const response = await api.get(`/v1/moments/popular-tags?moment_type=${moment_type}&user_id=1`);
    return response;
  } catch (error) {
    console.error('获取热门标签失败:', error);
    throw error;
  }
};

// ==================== 发布动态 API ====================

/**
 * 发布动态
 * @param {Object} dynamicData - 动态数据
 * @param {string} dynamicData.content - 内容
 * @param {Array<string>} dynamicData.tags - 标签
 * @param {string} dynamicData.image_url - 图片URL（可选）
 * @returns {Promise}
 */
export const publishDynamic = async (dynamicData) => {
  try {
    const data = {
      type: 0, // 0-动态
      content: dynamicData.content,
      tags: dynamicData.tags || [],
      image_url: dynamicData.image_url || null
    };
    
    const response = await api.post('/v1/moments?user_id=1', data);
    return response;
  } catch (error) {
    console.error('发布动态失败:', error);
    throw error;
  }
};

/**
 * 发布干货
 * @param {Object} dryGoodsData - 干货数据
 * @param {string} dryGoodsData.title - 标题
 * @param {string} dryGoodsData.content - 内容
 * @param {Array<string>} dryGoodsData.tags - 标签
 * @param {string} dryGoodsData.image_url - 图片URL（可选）
 * @returns {Promise}
 */
export const publishDryGoods = async (dryGoodsData) => {
  try {
    const data = {
      type: 1, // 1-干货
      title: dryGoodsData.title,
      content: dryGoodsData.content,
      tags: dryGoodsData.tags || [],
      image_url: dryGoodsData.image_url || null
    };
    
    const response = await api.post('/v1/moments?user_id=1', data);
    return response;
  } catch (error) {
    console.error('发布干货失败:', error);
    throw error;
  }
};

// ==================== 互动 API ====================

/**
 * 点赞/取消点赞
 * @param {number} momentId - 动态ID
 * @returns {Promise}
 */
export const toggleLike = async (momentId) => {
  try {
    const response = await api.post(`/v1/moments/${momentId}/like?user_id=1`);
    return response;
  } catch (error) {
    console.error('点赞操作失败:', error);
    throw error;
  }
};

/**
 * 获取评论列表
 * @param {number} momentId - 动态ID
 * @param {number} page - 页码
 * @param {number} page_size - 每页数量
 * @returns {Promise}
 */
export const getComments = async (momentId, page = 1, page_size = 20) => {
  try {
    const response = await api.get(`/v1/moments/${momentId}/comments?user_id=1&page=${page}&page_size=${page_size}`);
    return response;
  } catch (error) {
    console.error('获取评论失败:', error);
    throw error;
  }
};

/**
 * 提交评论
 * @param {number} momentId - 动态ID
 * @param {string} content - 评论内容
 * @returns {Promise}
 */
export const submitComment = async (momentId, content) => {
  try {
    const response = await api.post(`/v1/moments/${momentId}/comments?user_id=1`, { content });
    return response;
  } catch (error) {
    console.error('提交评论失败:', error);
    throw error;
  }
};

/**
 * 分享动态
 * @param {number} momentId - 动态ID
 * @returns {Promise}
 */
export const shareMoment = async (momentId) => {
  try {
    const response = await api.post(`/v1/moments/${momentId}/share?user_id=1`);
    return response;
  } catch (error) {
    console.error('分享失败:', error);
    throw error;
  }
};

/**
 * 收藏/取消收藏
 * @param {number} momentId - 动态ID
 * @returns {Promise}
 */
export const toggleBookmark = async (momentId) => {
  try {
    const response = await api.post(`/v1/moments/${momentId}/bookmark?user_id=1`);
    return response;
  } catch (error) {
    console.error('收藏操作失败:', error);
    throw error;
  }
};

// 导出默认对象
export default {
  getMomentList,
  searchMoments,
  getPopularTags,
  publishDynamic,
  publishDryGoods,
  toggleLike,
  getComments,
  submitComment,
  shareMoment,
  toggleBookmark
}; 