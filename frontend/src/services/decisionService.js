/**
 * 决策服务
 * 处理与后端的 API 通信
 */
import { buildApiUrl, getAuthHeaders, handleApiError, API_ENDPOINTS } from '../config/api';

class DecisionService {
  constructor() {
    this.baseUrl = buildApiUrl('');
  }

  /**
   * 发送 HTTP 请求
   * @param {string} endpoint - API 端点
   * @param {object} options - 请求选项
   * @returns {Promise} 响应数据
   */
  async request(endpoint, options = {}) {
    const url = buildApiUrl(endpoint);
    const config = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw {
          response: {
            data: errorData,
            status: response.status,
          }
        };
      }

      return await response.json();
    } catch (error) {
      throw handleApiError(error);
    }
  }

  /**
   * 健康检查
   * @returns {Promise} 健康状态
   */
  async healthCheck() {
    return this.request(API_ENDPOINTS.HEALTH);
  }

  /**
   * 测试连接
   * @returns {Promise} 测试结果
   */
  async testConnection() {
    return this.request(API_ENDPOINTS.TEST);
  }

  /**
   * 用户注册
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @returns {Promise} 注册结果
   */
  async register(username, password) {
    return this.request(API_ENDPOINTS.REGISTER, {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  /**
   * 用户登录
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @returns {Promise} 登录结果
   */
  async login(username, password) {
    return this.request(API_ENDPOINTS.LOGIN, {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  }

  /**
   * 用户退出
   * @param {string} token - 访问令牌
   * @returns {Promise} 退出结果
   */
  async logout(token) {
    return this.request(API_ENDPOINTS.LOGOUT, {
      method: 'POST',
      headers: getAuthHeaders(token),
    });
  }

  /**
   * 获取当前用户信息
   * @param {string} token - 访问令牌
   * @returns {Promise} 用户信息
   */
  async getCurrentUser(token) {
    return this.request(API_ENDPOINTS.ME, {
      method: 'GET',
      headers: getAuthHeaders(token),
    });
  }

  /**
   * 决策分析
   * @param {string} description - 决策描述
   * @param {Array} options - 可选方案
   * @param {string} token - 访问令牌（可选）
   * @returns {Promise} 分析结果
   */
  async analyzeDecision(description, options = [], token = null) {
    const headers = token ? getAuthHeaders(token) : { 'Content-Type': 'application/json' };
    
    return this.request(API_ENDPOINTS.DECISION, {
      method: 'POST',
      headers,
      body: JSON.stringify({ description, options }),
    });
  }

  /**
   * 聊天对话
   * @param {string} message - 用户消息
   * @param {string} sessionId - 会话ID
   * @param {string} token - 访问令牌（可选）
   * @returns {Promise} 聊天响应
   */
  async chat(message, sessionId = 'default', token = null) {
    const headers = token ? getAuthHeaders(token) : { 'Content-Type': 'application/json' };
    
    return this.request(API_ENDPOINTS.CHAT, {
      method: 'POST',
      headers,
      body: JSON.stringify({ message, session_id: sessionId }),
    });
  }
}

// 创建单例实例
const decisionService = new DecisionService();

export default decisionService;
