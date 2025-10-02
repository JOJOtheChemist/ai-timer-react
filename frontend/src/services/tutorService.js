import api from './api';

// ==================== 导师列表 API ====================

/**
 * 获取导师列表
 * @param {Object} filters - 筛选参数
 * @param {string} filters.tutor_type - 导师类型
 * @param {string} filters.domain - 擅长领域
 * @param {string} filters.price_range - 价格区间
 * @param {string} filters.sort_by - 排序方式
 * @param {number} filters.page - 页码
 * @param {number} filters.page_size - 每页数量
 * @returns {Promise}
 */
export const getTutorList = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    
    // 必需参数：user_id（开发环境使用固定值）
    const userId = filters.user_id || 1;
    params.append('user_id', userId);
    
    // 添加筛选参数
    if (filters.tutor_type && filters.tutor_type !== '全部') {
      params.append('tutor_type', filters.tutor_type);
    }
    if (filters.domain && filters.domain !== '全部') {
      params.append('domain', filters.domain);
    }
    if (filters.price_range && filters.price_range !== '全部') {
      params.append('price_range', filters.price_range);
    }
    
    // 排序参数
    if (filters.sort_by) {
      params.append('sort_by', filters.sort_by);
    }
    
    // 分页参数
    if (filters.page) {
      params.append('page', filters.page);
    }
    if (filters.page_size) {
      params.append('page_size', filters.page_size);
    }
    
    const queryString = params.toString();
    const url = `/v1/tutors/?${queryString}`;
    
    const response = await api.get(url);
    return response;
  } catch (error) {
    console.error('获取导师列表失败:', error);
    throw error;
  }
};

/**
 * 搜索导师
 * @param {string} keyword - 搜索关键词
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const searchTutors = async (keyword, userId = 1) => {
  try {
    const response = await api.get(`/v1/tutors/search?user_id=${userId}&keyword=${encodeURIComponent(keyword)}`);
    return response;
  } catch (error) {
    console.error('搜索导师失败:', error);
    throw error;
  }
};

/**
 * 获取导师领域列表
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const getTutorDomains = async (userId = 1) => {
  try {
    const response = await api.get(`/v1/tutors/domains?user_id=${userId}`);
    return response;
  } catch (error) {
    console.error('获取导师领域失败:', error);
    throw error;
  }
};

// ==================== 导师详情 API ====================

/**
 * 获取导师详情
 * @param {number} tutorId - 导师ID
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const getTutorDetail = async (tutorId, userId = 1) => {
  try {
    const response = await api.get(`/v1/tutors/${tutorId}?user_id=${userId}`);
    return response;
  } catch (error) {
    console.error('获取导师详情失败:', error);
    throw error;
  }
};

/**
 * 获取导师服务列表
 * @param {number} tutorId - 导师ID
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const getTutorServices = async (tutorId, userId = 1) => {
  try {
    const response = await api.get(`/v1/tutors/${tutorId}/services?user_id=${userId}`);
    return response;
  } catch (error) {
    console.error('获取导师服务失败:', error);
    throw error;
  }
};

// ==================== 导师互动 API ====================

/**
 * 关注/取消关注导师
 * @param {number} tutorId - 导师ID
 * @param {number} userId - 用户ID
 * @param {boolean} isFollow - true为关注，false为取消关注
 * @returns {Promise}
 */
export const toggleTutorFollow = async (tutorId, userId = 1, isFollow = true) => {
  try {
    if (isFollow) {
      const response = await api.post(`/v1/users/me/relations/follow/tutor/${tutorId}?user_id=${userId}`);
      return response;
    } else {
      const response = await api.delete(`/v1/users/me/relations/follow/tutor/${tutorId}?user_id=${userId}`);
      return response;
    }
  } catch (error) {
    console.error('关注导师操作失败:', error);
    throw error;
  }
};

/**
 * 向导师发送私信
 * @param {number} tutorId - 导师ID
 * @param {string} content - 私信内容
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const sendTutorMessage = async (tutorId, content, userId = 1) => {
  try {
    const response = await api.post(
      `/v1/users/me/relations/message/tutor/${tutorId}?user_id=${userId}`,
      { content }
    );
    return response;
  } catch (error) {
    console.error('发送私信失败:', error);
    throw error;
  }
};

/**
 * 购买导师服务
 * @param {number} tutorId - 导师ID
 * @param {number} serviceId - 服务ID
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export const purchaseTutorService = async (tutorId, serviceId, userId = 1) => {
  try {
    const response = await api.post(
      `/v1/users/me/assets/purchase?user_id=${userId}`,
      { tutor_id: tutorId, service_id: serviceId }
    );
    return response;
  } catch (error) {
    console.error('购买服务失败:', error);
    throw error;
  }
};

// 导出默认对象
export default {
  getTutorList,
  searchTutors,
  getTutorDomains,
  getTutorDetail,
  getTutorServices,
  toggleTutorFollow,
  sendTutorMessage,
  purchaseTutorService
}; 