import { api } from './api';

// 用户相关API服务
export const userService = {
  // 用户登录
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    if (response.token) {
      localStorage.setItem('authToken', response.token);
      localStorage.setItem('userInfo', JSON.stringify(response.user));
    }
    return response;
  },

  // 用户注册
  register: async (userData) => {
    return await api.post('/auth/register', userData);
  },

  // 用户登出
  logout: () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userInfo');
  },

  // 获取当前用户信息
  getCurrentUser: () => {
    const userInfo = localStorage.getItem('userInfo');
    return userInfo ? JSON.parse(userInfo) : null;
  },

  // 更新用户信息
  updateProfile: async (userId, profileData) => {
    return await api.put(`/users/${userId}`, profileData);
  },

  // 获取用户详细信息
  getUserProfile: async (userId) => {
    return await api.get(`/users/${userId}`);
  },

  // 获取用户学习统计
  getUserStats: async (userId) => {
    return await api.get(`/users/${userId}/stats`);
  },

  // 获取用户排行榜数据
  getLeaderboard: async (type = 'weekly', limit = 100) => {
    return await api.get(`/users/leaderboard?type=${type}&limit=${limit}`);
  },

  // 关注/取消关注用户
  toggleFollow: async (targetUserId) => {
    return await api.post(`/users/follow/${targetUserId}`);
  },
};

export default userService; 