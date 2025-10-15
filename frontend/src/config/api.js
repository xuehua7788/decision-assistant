/**
 * API 配置文件
 * 管理前后端 API 连接
 */

// 获取环境变量中的 API URL
const getApiUrl = () => {
  // 开发环境
  if (process.env.NODE_ENV === 'development') {
    return process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }
  
  // 生产环境
  return process.env.REACT_APP_API_URL || 'https://decision-assistant-api.onrender.com';
};

// API 基础配置
export const API_CONFIG = {
  BASE_URL: getApiUrl(),
  TIMEOUT: 30000, // 30秒超时
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
};

// API 端点
export const API_ENDPOINTS = {
  // 基础端点
  HEALTH: '/health',
  TEST: '/api/test',
  
  // 认证端点
  REGISTER: '/api/auth/register',
  LOGIN: '/api/auth/login',
  LOGOUT: '/api/auth/logout',
  ME: '/api/auth/me',
  
  // 功能端点
  DECISION: '/api/decision',
  CHAT: '/api/chat',
};

// 构建完整的 API URL
export const buildApiUrl = (endpoint) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// 获取认证头
export const getAuthHeaders = (token) => {
  return {
    ...API_CONFIG.HEADERS,
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

// 错误处理
export const handleApiError = (error) => {
  console.error('API Error:', error);
  
  if (error.response) {
    // 服务器响应了错误状态码
    return {
      message: error.response.data?.error || '服务器错误',
      status: error.response.status,
    };
  } else if (error.request) {
    // 请求已发出但没有收到响应
    return {
      message: '无法连接到服务器，请检查网络连接',
      status: 0,
    };
  } else {
    // 其他错误
    return {
      message: '请求配置错误',
      status: 0,
    };
  }
};

// 默认导出
export default {
  API_CONFIG,
  API_ENDPOINTS,
  buildApiUrl,
  getAuthHeaders,
  handleApiError,
};
