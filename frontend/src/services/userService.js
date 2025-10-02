import api from './api';

const userService = {
  // 获取当前用户个人信息
  getCurrentUserProfile: async (userId) => {
    const response = await api.get('/users/me/profile', {
      params: { user_id: userId }
    });
    return response;
  },

  // 更新当前用户个人信息
  updateCurrentUserProfile: async (userId, profileData) => {
    const response = await api.put('/users/me/profile', profileData, {
      params: { user_id: userId }
    });
    return response;
  },

  // 获取用户资产信息
  getUserAssets: async (userId) => {
    const response = await api.get('/users/me/assets', {
      params: { user_id: userId }
    });
    return response;
  },

  // 获取用户关系统计
  getRelationStats: async (userId) => {
    const response = await api.get('/users/me/relations/stats', {
      params: { user_id: userId }
    });
    return response;
  },

  // 获取关注的导师列表
  getFollowedTutors: async (userId, limit = 3) => {
    const response = await api.get('/users/me/relations/tutors', {
      params: { user_id: userId, limit }
    });
    return response;
  },

  // 获取粉丝列表
  getRecentFans: async (userId, limit = 4) => {
    const response = await api.get('/users/me/relations/fans', {
      params: { user_id: userId, limit }
    });
    return response;
  },

  // 获取用户徽章
  getUserBadges: async (userId) => {
    const response = await api.get('/badges/my', {
      params: { user_id: userId }
    });
    return response;
  }
};

export default userService; 