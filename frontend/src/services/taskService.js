import { api } from './api';

// 任务相关API服务
export const taskService = {
  // 获取任务列表
  getTasks: async (userId) => {
    return await api.get(`/tasks/${userId}`);
  },

  // 创建新任务
  createTask: async (taskData) => {
    return await api.post('/tasks', taskData);
  },

  // 更新任务状态
  updateTaskStatus: async (taskId, status) => {
    return await api.put(`/tasks/${taskId}/status`, { status });
  },

  // 更新任务详情
  updateTask: async (taskId, taskData) => {
    return await api.put(`/tasks/${taskId}`, taskData);
  },

  // 删除任务
  deleteTask: async (taskId) => {
    return await api.delete(`/tasks/${taskId}`);
  },

  // 获取任务统计数据
  getTaskStats: async (userId, timeRange) => {
    return await api.get(`/tasks/stats/${userId}?range=${timeRange}`);
  },

  // 获取时间热力图数据
  getHeatmapData: async (userId, startDate, endDate) => {
    return await api.get(`/tasks/heatmap/${userId}?start=${startDate}&end=${endDate}`);
  },
};

export default taskService; 