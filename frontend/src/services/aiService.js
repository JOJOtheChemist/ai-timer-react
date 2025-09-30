import { api } from './api';

// AI相关API服务
export const aiService = {
  // 发送AI对话消息
  sendMessage: async (message, conversationId = null) => {
    return await api.post('/ai/chat', {
      message,
      conversationId,
    });
  },

  // 获取对话历史
  getConversationHistory: async (conversationId) => {
    return await api.get(`/ai/conversations/${conversationId}`);
  },

  // 获取用户的所有对话列表
  getConversations: async (userId) => {
    return await api.get(`/ai/conversations/user/${userId}`);
  },

  // 创建新对话
  createConversation: async (title) => {
    return await api.post('/ai/conversations', { title });
  },

  // 删除对话
  deleteConversation: async (conversationId) => {
    return await api.delete(`/ai/conversations/${conversationId}`);
  },

  // 获取AI学习分析
  getStudyAnalysis: async (userId, timeRange) => {
    return await api.get(`/ai/analysis/${userId}?range=${timeRange}`);
  },

  // 获取AI学习建议
  getStudySuggestions: async (userId, currentTask) => {
    return await api.post('/ai/suggestions', {
      userId,
      currentTask,
    });
  },

  // 获取注意力分析
  getAttentionAnalysis: async (userId, date) => {
    return await api.get(`/ai/attention/${userId}?date=${date}`);
  },
};

export default aiService; 