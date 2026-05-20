import Taro from '@tarojs/taro';
import { getStudentId } from '../utils/auth';

// API_URL 由 Taro defineConstants 在编译时注入
// development: http://localhost:8000/api
// production:  构建时配置的生产地址
declare const API_URL: string;

const BASE_URL = API_URL || 'http://localhost:8000/api';

interface RequestOptions {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: any;
  header?: Record<string, string>;
}

export async function request<T = any>(options: RequestOptions): Promise<T> {
  const { url, method = 'GET', data, header = {} } = options;

  try {
    const res = await Taro.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        'X-Student-Id': getStudentId(),
        ...header,
      },
    });

    if (res.statusCode >= 200 && res.statusCode < 300) {
      return res.data as T;
    }
    throw new Error(res.data?.detail || '请求失败');
  } catch (err) {
    console.error('API请求失败:', err);
    throw err;
  }
}
