import api from './api';

/**
 * Success Case Service - 成功案例页相关的所有API调用
 */

// ==================== 热门案例 API ====================

/**
 * 获取热门推荐案例
 * @param {number} limit - 限制返回数量，默认3个
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const getHotCases = async (limit = 3, userId = 1) => {
  try {
    const response = await api.get(`/cases/hot?user_id=${userId}&limit=${limit}`);
    return response;
  } catch (error) {
    console.error('获取热门案例失败:', error);
    throw error;
  }
};

// ==================== 案例列表 API ====================

/**
 * 获取案例列表（支持筛选）
 * @param {Object} filters - 筛选参数
 * @param {string} filters.category - 目标分类（高考、考研、考证等）
 * @param {string} filters.duration - 投入时长范围
 * @param {string} filters.experience - 特殊经历
 * @param {string} filters.foundation - 初始基础
 * @param {number} filters.skip - 跳过数量（分页）
 * @param {number} filters.limit - 每页数量
 * @returns {Promise}
 */
export const getCaseList = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    
    // 必需参数：user_id（开发环境使用固定值）
    const userId = filters.user_id || 1; // TODO: 从认证系统获取
    params.append('user_id', userId);
    
    // 添加筛选参数
    if (filters.category && filters.category !== '全部') {
      params.append('category', filters.category);
    }
    if (filters.duration && filters.duration !== '全部') {
      params.append('duration', filters.duration);
    }
    if (filters.experience && filters.experience !== '全部') {
      params.append('experience', filters.experience);
    }
    if (filters.foundation && filters.foundation !== '全部') {
      params.append('foundation', filters.foundation);
    }
    
    // 分页参数
    if (filters.skip !== undefined) {
      params.append('skip', filters.skip);
    }
    if (filters.limit) {
      params.append('limit', filters.limit);
    }
    
    const queryString = params.toString();
    const url = `/cases/?${queryString}`; // 注意添加了斜杠
    
    const response = await api.get(url);
    return response;
  } catch (error) {
    console.error('获取案例列表失败:', error);
    throw error;
  }
};

// ==================== 搜索 API ====================

/**
 * 搜索案例
 * @param {string} keyword - 搜索关键词
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const searchCases = async (keyword, userId = 1) => {
  try {
    const response = await api.get(`/cases/search?user_id=${userId}&keyword=${encodeURIComponent(keyword)}`);
    return response;
  } catch (error) {
    console.error('搜索案例失败:', error);
    throw error;
  }
};

// ==================== 案例详情 API ====================

/**
 * 获取案例详情
 * @param {number} caseId - 案例ID
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const getCaseDetail = async (caseId, userId = 1) => {
  try {
    const response = await api.get(`/cases/${caseId}?user_id=${userId}`);
    return response;
  } catch (error) {
    console.error('获取案例详情失败:', error);
    throw error;
  }
};

/**
 * 获取案例权限信息
 * @param {number} caseId - 案例ID
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const getCasePermission = async (caseId, userId) => {
  try {
    const response = await api.get(`/cases/${caseId}/permission?user_id=${userId}`);
    return response;
  } catch (error) {
    console.error('获取案例权限失败:', error);
    throw error;
  }
};

// ==================== 用户信息 API ====================

/**
 * 获取用户简易信息（仅公开信息）
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const getUserSimpleInfo = async (userId) => {
  try {
    const response = await api.get(`/users/${userId}/simple-info`);
    return response;
  } catch (error) {
    console.error('获取用户信息失败:', error);
    throw error;
  }
};

export default {
  getHotCases,
  getCaseList,
  searchCases,
  getCaseDetail,
  getCasePermission,
  getUserSimpleInfo
}; 