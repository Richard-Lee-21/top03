// API响应类型
export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
}

// 商品推荐类型
export interface ProductRecommendation {
  rank: number;
  product_name: string;
  description: string;
  source_link: string;
  price?: string;
  rating?: number;
  image_url?: string;
  pros?: string[];
  cons?: string[];
  best_for?: string;
}

// 搜索请求类型
export interface SearchRequest {
  keyword: string;
}

// 搜索响应类型
export interface SearchResponse {
  products: ProductRecommendation[];
  total_results: number;
  search_time: number;
  cached: boolean;
}

// 配置类型
export interface Configuration {
  id: number;
  key: string;
  value: string;
  group: 'api' | 'prompt' | 'ui' | 'cache';
  updated_at: string;
}

// 管理员登录类型
export interface AdminLoginRequest {
  username: string;
  password: string;
}

export interface AdminLoginResponse {
  status: 'success';
  token: string;
  expires_in: number;
}

// 配置更新类型
export interface ConfigurationUpdate {
  settings: {
    key: string;
    value: string;
  }[];
}

// LLM工具调用类型
export interface LLMToolCall {
  name: string;
  input: {
    products: Array<{
      rank: number;
      product_name: string;
      description: string;
      source_link: string;
      price?: string;
      rating?: number;
      pros?: string[];
      cons?: string[];
      best_for?: string;
    }>;
  };
}

// 搜索结果类型（来自Serper API）
export interface SearchResult {
  title: string;
  link: string;
  snippet: string;
  position: number;
  favicon?: string;
  date?: string;
}

// 错误类型
export interface AppError {
  code: string;
  message: string;
  details?: any;
}

// 用户偏好设置
export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: 'zh-CN' | 'en-US';
  auto_search: boolean;
  show_ratings: boolean;
  show_prices: boolean;
}