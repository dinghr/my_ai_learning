import { request } from './request';
import { getStudentId } from '../utils/auth';

export interface Task {
  id: string;
  name: string;
  description?: string;
  icon: string;
  task_type: 'daily' | 'long_term';
  category: string;
  points: number;
  target_value?: number;
  current_value: number;
  unit?: string;
  is_active: boolean;
  sort_order: number;
  is_completed_today: boolean;
  today_completion_id?: string;
}

export interface DailyProgress {
  total: number;
  completed: number;
  percentage: number;
  points_today: number;
}

function getUrl(path: string) {
  return `/students/${getStudentId() || 'demo-student'}${path}`;
}

export function getTasks(taskType?: 'daily' | 'long_term') {
  const params = taskType ? `?task_type=${taskType}` : '';
  return request<Task[]>({
    url: getUrl(`/tasks${params}`),
  });
}

export function completeTask(taskId: string, note?: string, progressIncrement?: number) {
  return request({
    url: getUrl(`/tasks/${taskId}/complete`),
    method: 'POST',
    data: { note, progress_increment: progressIncrement },
  });
}

export function getDailyProgress() {
  return request<DailyProgress>({
    url: getUrl('/tasks/progress/daily'),
  });
}

export interface TaskCreateData {
  name: string;
  description?: string;
  icon?: string;
  task_type: 'daily' | 'long_term';
  category?: string;
  points?: number;
  target_value?: number;
  unit?: string;
}

export function createTask(data: TaskCreateData) {
  return request<Task>({
    url: getUrl('/tasks'),
    method: 'POST',
    data,
  });
}
