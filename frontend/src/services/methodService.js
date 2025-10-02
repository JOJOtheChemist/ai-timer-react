import api from './api';

// ==================== 学习方法列表 API ====================

/**
 * 获取学习方法列表
 * @param {Object} filters - 筛选参数
 * @param {string} filters.category - 方法分类
 * @param {number} filters.page - 页码
 * @param {number} filters.page_size - 每页数量
 * @returns {Promise}
 */
export const getMethodList = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    
    // 必需参数：user_id（开发环境使用固定值）
    const userId = filters.user_id || 1;
    params.append('user_id', userId);
    
    // 添加筛选参数
    if (filters.category && filters.category !== '全部方法') {
      params.append('category', filters.category);
    }
    
    // 分页参数
    if (filters.page) {
      params.append('page', filters.page);
    }
    if (filters.page_size) {
      params.append('page_size', filters.page_size);
    }
    
    const queryString = params.toString();
    const url = `/methods/?${queryString}`;
    
    const response = await api.get(url);
    return response;
  } catch (error) {
    console.error('获取学习方法列表失败:', error);
    throw error;
  }
};

/**
 * 获取学习方法详情
 * @param {number} methodId - 方法ID
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const getMethodDetail = async (methodId, userId = 1) => {
  try {
    const response = await api.get(`/methods/${methodId}?user_id=${userId}`);
    return response;
  } catch (error) {
    console.error('获取学习方法详情失败:', error);
    throw error;
  }
};

// ==================== AI推荐 API ====================

/**
 * 获取AI推荐的学习方法
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const getAIRecommendation = async (userId = 1) => {
  try {
    const response = await api.get(`/ai/recommendations/method?user_id=${userId}`);
    return response;
  } catch (error) {
    console.error('获取AI推荐失败:', error);
    throw error;
  }
};

// ==================== 打卡 API ====================

/**
 * 提交学习方法打卡
 * @param {number} methodId - 方法ID
 * @param {Object} checkinData - 打卡数据
 * @param {string} checkinData.checkin_type - 打卡类型（正字打卡/计数打卡）
 * @param {number} checkinData.progress - 打卡进度（1-4）
 * @param {string} checkinData.note - 打卡心得
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const submitCheckin = async (methodId, checkinData, userId = 1) => {
  try {
    const response = await api.post(
      `/methods/${methodId}/checkin?user_id=${userId}`,
      checkinData
    );
    return response;
  } catch (error) {
    console.error('提交打卡失败:', error);
    throw error;
  }
};

/**
 * 获取用户打卡历史
 * @param {number} methodId - 方法ID
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const getCheckinHistory = async (methodId, userId = 1) => {
  try {
    const response = await api.get(`/methods/${methodId}/checkins/history?user_id=${userId}`);
    return response;
  } catch (error) {
    console.error('获取打卡历史失败:', error);
    throw error;
  }
};

// 导出默认对象
export default {
  getMethodList,
  getMethodDetail,
  getAIRecommendation,
  submitCheckin,
  getCheckinHistory
}; 