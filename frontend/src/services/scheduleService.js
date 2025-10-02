import api from './api';

/**
 * Schedule Service - 首页相关的所有API调用
 */

// ==================== 任务相关 API ====================

/**
 * 获取任务列表
 * @param {Object} params - 查询参数
 * @param {string} params.category - 任务分类筛选
 * @param {string} params.task_type - 任务类型筛选 (study/life/work/play)
 * @param {number} params.user_id - 用户ID
 * @returns {Promise}
 */
export const getTaskList = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString();
    const response = await api.get(`/tasks?${queryString}`);
    return response;
  } catch (error) {
    console.error('获取任务列表失败:', error);
    throw error;
  }
};

/**
 * 创建新任务
 * @param {Object} taskData - 任务数据
 * @param {number} user_id - 用户ID
 * @returns {Promise}
 */
export const createTask = async (taskData, user_id) => {
  try {
    const response = await api.post(`/tasks?user_id=${user_id}`, taskData);
    return response;
  } catch (error) {
    console.error('创建任务失败:', error);
    throw error;
  }
};

/**
 * 快捷添加任务
 * @param {string} taskName - 任务名称
 * @param {number} user_id - 用户ID
 * @returns {Promise}
 */
export const quickAddTask = async (taskName, user_id) => {
  try {
    const response = await api.post(`/tasks/quick-add?user_id=${user_id}`, {
      name: taskName,
      type: 'study'
    });
    return response;
  } catch (error) {
    console.error('快速添加任务失败:', error);
    throw error;
  }
};

/**
 * 更新任务
 * @param {number} taskId - 任务ID
 * @param {Object} taskData - 更新数据
 * @param {number} user_id - 用户ID
 * @returns {Promise}
 */
export const updateTask = async (taskId, taskData, user_id) => {
  try {
    const response = await api.patch(`/tasks/${taskId}?user_id=${user_id}`, taskData);
    return response;
  } catch (error) {
    console.error('更新任务失败:', error);
    throw error;
  }
};

/**
 * 删除任务
 * @param {number} taskId - 任务ID
 * @param {number} user_id - 用户ID
 * @returns {Promise}
 */
export const deleteTask = async (taskId, user_id) => {
  try {
    const response = await api.delete(`/tasks/${taskId}?user_id=${user_id}`);
    return response;
  } catch (error) {
    console.error('删除任务失败:', error);
    throw error;
  }
};

// ==================== 时间表相关 API ====================

/**
 * 获取今日时间表
 * @param {number} user_id - 用户ID
 * @param {string} target_date - 目标日期 (YYYY-MM-DD)
 * @returns {Promise}
 */
export const getTodayTimeSlots = async (user_id, target_date = null) => {
  try {
    const params = { user_id };
    if (target_date) params.target_date = target_date;
    const queryString = new URLSearchParams(params).toString();
    
    const response = await api.get(`/schedule/time-slots?${queryString}`);
    return response;
  } catch (error) {
    console.error('获取时间表失败:', error);
    throw error;
  }
};

/**
 * 保存心情记录
 * @param {number} slotId - 时间段ID
 * @param {string} mood - 心情类型 (happy/focused/tired)
 * @param {number} user_id - 用户ID
 * @returns {Promise}
 */
export const saveMoodRecord = async (slotId, mood, user_id) => {
  try {
    const response = await api.post(
      `/schedule/time-slots/${slotId}/mood?user_id=${user_id}`,
      { mood }
    );
    return response;
  } catch (error) {
    console.error('保存心情记录失败:', error);
    throw error;
  }
};

/**
 * 为时间段绑定任务
 * @param {number} slotId - 时间段ID
 * @param {number} taskId - 任务ID
 * @param {number} user_id - 用户ID
 * @returns {Promise}
 */
export const bindTaskToSlot = async (slotId, taskId, user_id) => {
  try {
    const response = await api.post(
      `/schedule/time-slots/${slotId}/task?user_id=${user_id}`,
      { task_id: taskId }
    );
    return response;
  } catch (error) {
    console.error('绑定任务失败:', error);
    throw error;
  }
};

/**
 * 完成时间段
 * @param {number} slotId - 时间段ID
 * @param {number} user_id - 用户ID
 * @returns {Promise}
 */
export const completeTimeSlot = async (slotId, user_id) => {
  try {
    const response = await api.patch(
      `/schedule/time-slots/${slotId}/complete?user_id=${user_id}`
    );
    return response;
  } catch (error) {
    console.error('完成时间段失败:', error);
    throw error;
  }
};

/**
 * 开始时间段
 * @param {number} slotId - 时间段ID
 * @param {number} user_id - 用户ID
 * @returns {Promise}
 */
export const startTimeSlot = async (slotId, user_id) => {
  try {
    const response = await api.patch(
      `/schedule/time-slots/${slotId}/start?user_id=${user_id}`
    );
    return response;
  } catch (error) {
    console.error('开始时间段失败:', error);
    throw error;
  }
};

// ==================== 统计相关 API ====================

/**
 * 获取本周统计概览
 * @param {number} user_id - 用户ID
 * @param {string} year_week - 年周 (如 '2025-01')
 * @returns {Promise}
 */
export const getWeeklyOverview = async (user_id, year_week = null) => {
  try {
    const params = { user_id };
    if (year_week) params.year_week = year_week;
    const queryString = new URLSearchParams(params).toString();
    
    const response = await api.get(`/statistics/weekly-overview?${queryString}`);
    return response;
  } catch (error) {
    console.error('获取周统计失败:', error);
    throw error;
  }
};

/**
 * 获取本周图表数据
 * @param {number} user_id - 用户ID
 * @param {string} year_week - 年周
 * @returns {Promise}
 */
export const getWeeklyChart = async (user_id, year_week = null) => {
  try {
    const params = { user_id };
    if (year_week) params.year_week = year_week;
    const queryString = new URLSearchParams(params).toString();
    
    const response = await api.get(`/statistics/weekly-chart?${queryString}`);
    return response;
  } catch (error) {
    console.error('获取图表数据失败:', error);
    throw error;
  }
};

/**
 * 获取仪表盘综合数据
 * @param {number} user_id - 用户ID
 * @returns {Promise}
 */
export const getDashboardData = async (user_id) => {
  try {
    const response = await api.get(`/statistics/dashboard?user_id=${user_id}`);
    return response;
  } catch (error) {
    console.error('获取仪表盘数据失败:', error);
    throw error;
  }
};

// ==================== AI推荐相关 API ====================

/**
 * 获取AI推荐的时间段
 * @param {number} user_id - 用户ID
 * @returns {Promise}
 */
export const getAIRecommendedSlots = async (user_id) => {
  try {
    const response = await api.get(`/schedule/time-slots/ai-recommended?user_id=${user_id}`);
    return response;
  } catch (error) {
    console.error('获取AI推荐失败:', error);
    throw error;
  }
};

/**
 * 获取个性化推荐
 * @param {number} user_id - 用户ID
 * @returns {Promise}
 */
export const getPersonalizedRecommendations = async (user_id) => {
  try {
    const response = await api.get(`/ai/recommendations/personalized?user_id=${user_id}`);
    return response;
  } catch (error) {
    console.error('获取个性化推荐失败:', error);
    throw error;
  }
};

/**
 * 采纳AI推荐
 * @param {number} recId - 推荐ID
 * @param {boolean} accept - 是否采纳
 * @param {number} user_id - 用户ID
 * @returns {Promise}
 */
export const acceptAIRecommendation = async (recId, accept, user_id) => {
  try {
    const response = await api.post(
      `/ai/recommendations/feedback?user_id=${user_id}`,
      {
        method_id: recId,
        feedback_type: accept ? 'helpful' : 'not_helpful'
      }
    );
    return response;
  } catch (error) {
    console.error('提交AI推荐反馈失败:', error);
    throw error;
  }
};

export default {
  // 任务相关
  getTaskList,
  createTask,
  quickAddTask,
  updateTask,
  deleteTask,
  
  // 时间表相关
  getTodayTimeSlots,
  saveMoodRecord,
  bindTaskToSlot,
  completeTimeSlot,
  startTimeSlot,
  
  // 统计相关
  getWeeklyOverview,
  getWeeklyChart,
  getDashboardData,
  
  // AI推荐相关
  getAIRecommendedSlots,
  getPersonalizedRecommendations,
  acceptAIRecommendation
}; 