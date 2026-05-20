import Taro from '@tarojs/taro';
import { request } from '../api/request';

const STORAGE_KEY = 'student_info';

export interface StudentInfo {
  student_id: string;
  openid: string;
  name: string;
  nickname?: string;
  points_balance: number;
}

/**
 * 获取本地存储的用户信息
 */
export function getStudentInfo(): StudentInfo | null {
  try {
    const data = Taro.getStorageSync(STORAGE_KEY);
    return data ? JSON.parse(data) : null;
  } catch {
    return null;
  }
}

/**
 * 保存用户信息到本地
 */
export function setStudentInfo(info: StudentInfo) {
  Taro.setStorageSync(STORAGE_KEY, JSON.stringify(info));
}

/**
 * 获取当前用户ID，如果未登录返回空字符串
 */
export function getStudentId(): string {
  const info = getStudentInfo();
  return info?.student_id || '';
}

/**
 * 检查是否已登录
 */
export function isLoggedIn(): boolean {
  return !!getStudentId();
}

/**
 * 微信小程序自动登录
 * 流程：wx.login 获取 code → 后端换取 openid → 自动创建/查找用户
 */
export async function wechatLogin(): Promise<StudentInfo | null> {
  // 先检查本地是否已有登录态
  const existing = getStudentInfo();
  if (existing?.student_id) {
    // 可选：向后端校验登录态是否有效
    return existing;
  }

  return new Promise((resolve) => {
    Taro.login({
      success: async (loginRes) => {
        if (loginRes.code) {
          try {
            const data = await request<StudentInfo>({
              url: '/wechat/login',
              method: 'POST',
              data: { code: loginRes.code },
            });
            setStudentInfo(data);
            resolve(data);
          } catch (err) {
            console.error('微信登录失败:', err);
            resolve(null);
          }
        } else {
          console.error('wx.login 失败:', loginRes);
          resolve(null);
        }
      },
      fail: (err) => {
        console.error('wx.login 调用失败:', err);
        resolve(null);
      },
    });
  });
}

/**
 * 退出登录（清除本地存储）
 */
export function logout() {
  Taro.removeStorageSync(STORAGE_KEY);
}
