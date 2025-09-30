import { api } from './api';

// 导师相关API服务
export const tutorService = {
  // 获取导师列表
  getTutors: async (filters = {}) => {
    const queryParams = new URLSearchParams(filters).toString();
    return await api.get(`/tutors?${queryParams}`);
  },

  // 获取导师详细信息
  getTutorProfile: async (tutorId) => {
    return await api.get(`/tutors/${tutorId}`);
  },

  // 获取导师的学生列表
  getTutorStudents: async (tutorId) => {
    return await api.get(`/tutors/${tutorId}/students`);
  },

  // 申请成为某导师的学生
  applyToTutor: async (tutorId, applicationData) => {
    return await api.post(`/tutors/${tutorId}/apply`, applicationData);
  },

  // 获取导师评论列表
  getTutorComments: async (tutorId, page = 1, limit = 10) => {
    return await api.get(`/tutors/${tutorId}/comments?page=${page}&limit=${limit}`);
  },

  // 添加导师评论
  addTutorComment: async (tutorId, commentData) => {
    return await api.post(`/tutors/${tutorId}/comments`, commentData);
  },

  // 给导师评分
  rateTutor: async (tutorId, rating) => {
    return await api.post(`/tutors/${tutorId}/rating`, { rating });
  },

  // 获取导师的课程/指导内容
  getTutorCourses: async (tutorId) => {
    return await api.get(`/tutors/${tutorId}/courses`);
  },

  // 预约导师指导时间
  bookTutorSession: async (tutorId, sessionData) => {
    return await api.post(`/tutors/${tutorId}/book`, sessionData);
  },

  // 获取用户的导师申请状态
  getApplicationStatus: async (userId, tutorId) => {
    return await api.get(`/tutors/applications/${userId}/${tutorId}`);
  },
};

export default tutorService; 