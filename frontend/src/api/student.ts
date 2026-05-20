import { request } from './request';

export interface Student {
  id: string;
  name: string;
  nickname?: string;
  age?: number;
  gender?: string;
  grade?: string;
  avatar?: string;
  points_balance: number;
}

export function getCurrentStudent() {
  return request<Student>({
    url: '/students/current',
  });
}
