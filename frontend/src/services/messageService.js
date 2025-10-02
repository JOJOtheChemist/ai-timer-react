import api from './api';

// 消息类型映射
const MESSAGE_TYPE_MAP = {
  'tutor': 0,
  'private': 1,
  'system': 2
};

const messageService = {
  // 获取消息列表
  getMessageList: async (params) => {
    const { message_type, page = 1, page_size = 20, user_id } = params;
    // 转换消息类型为数字
    const typeValue = typeof message_type === 'string' ? MESSAGE_TYPE_MAP[message_type] : message_type;
    
    const response = await api.get('/messages', {
      params: {
        message_type: typeValue,
        page,
        page_size,
        user_id
      }
    });
    return response;
  },

  // 获取消息详情
  getMessageDetail: async (messageId, userId) => {
    const response = await api.get(`/messages/${messageId}`, {
      params: { user_id: userId }
    });
    return response;
  },

  // 获取未读统计
  getUnreadStats: async (userId) => {
    const response = await api.get('/messages/unread-stats', {
      params: { user_id: userId }
    });
    return response;
  },

  // 标记消息为已读
  markAsRead: async (messageId, userId) => {
    const response = await api.post(`/messages/${messageId}/mark-read`, null, {
      params: { user_id: userId }
    });
    return response;
  },

  // 回复消息
  replyMessage: async (messageId, content, userId) => {
    const response = await api.post(`/messages/${messageId}/reply`, {
      content
    }, {
      params: { user_id: userId }
    });
    return response;
  },

  // 获取对话历史
  getConversationHistory: async (otherUserId, userId, limit = 10) => {
    const response = await api.get(`/messages/conversation/${otherUserId}`, {
      params: {
        user_id: userId,
        limit
      }
    });
    return response;
  }
};

export default messageService; 