import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  ApiResponse,
  SearchRequest,
  SearchResponse,
  Configuration,
  AdminLoginRequest,
  AdminLoginResponse,
  ConfigurationUpdate
} from '@/types';

// API客户端配置
class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.token = null;
          // 可以在这里触发重新登录逻辑
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
  }

  clearToken() {
    this.token = null;
  }

  // 获取商品推荐
  async getTopProducts(request: SearchRequest): Promise<SearchResponse> {
    try {
      const response = await this.client.post<ApiResponse<SearchResponse>>(
        '/api/get-top3',
        request
      );

      if (response.data.status === 'success' && response.data.data) {
        return response.data.data;
      }

      throw new Error(response.data.message || '获取推荐失败');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || error.message;
        throw new Error(`网络错误: ${message}`);
      }
      throw error;
    }
  }

  // 管理员登录
  async adminLogin(request: AdminLoginRequest): Promise<AdminLoginResponse> {
    try {
      const response = await this.client.post<ApiResponse<AdminLoginResponse>>(
        '/api/admin/login',
        request
      );

      if (response.data.status === 'success' && response.data.data) {
        this.setToken(response.data.data.token);
        return response.data.data;
      }

      throw new Error(response.data.message || '登录失败');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || error.message;
        throw new Error(`登录失败: ${message}`);
      }
      throw error;
    }
  }

  // 获取所有配置
  async getConfigurations(): Promise<Configuration[]> {
    try {
      const response = await this.client.get<ApiResponse<Configuration[]>>(
        '/api/admin/settings'
      );

      if (response.data.status === 'success' && response.data.data) {
        return response.data.data;
      }

      throw new Error(response.data.message || '获取配置失败');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || error.message;
        throw new Error(`获取配置失败: ${message}`);
      }
      throw error;
    }
  }

  // 更新配置
  async updateConfigurations(request: ConfigurationUpdate): Promise<void> {
    try {
      const response = await this.client.post<ApiResponse>(
        '/api/admin/settings',
        request
      );

      if (response.data.status !== 'success') {
        throw new Error(response.data.message || '更新配置失败');
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = error.response?.data?.message || error.message;
        throw new Error(`更新配置失败: ${message}`);
      }
      throw error;
    }
  }

  // 测试API连接
  async testConnection(): Promise<boolean> {
    try {
      await this.client.get('/api/health');
      return true;
    } catch {
      return false;
    }
  }

  // 登出
  logout() {
    this.clearToken();
  }
}

// 创建单例实例
export const apiClient = new ApiClient();

// 导出便捷方法
export const api = {
  getTopProducts: (request: SearchRequest) => apiClient.getTopProducts(request),
  adminLogin: (request: AdminLoginRequest) => apiClient.adminLogin(request),
  getConfigurations: () => apiClient.getConfigurations(),
  updateConfigurations: (request: ConfigurationUpdate) => apiClient.updateConfigurations(request),
  testConnection: () => apiClient.testConnection(),
  setToken: (token: string) => apiClient.setToken(token),
  logout: () => apiClient.logout(),
};