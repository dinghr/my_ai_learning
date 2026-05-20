import { request } from './request';
import { getStudentId } from '../utils/auth';

export interface PointsSummary {
  balance: number;
  total_earned: number;
  total_spent: number;
}

export interface PointsRecord {
  id: string;
  points: number;
  balance: number;
  source_type: string;
  description?: string;
  created_at: string;
}

function getUrl(path: string) {
  return `/students/${getStudentId() || 'demo-student'}${path}`;
}

export function getPointsSummary() {
  return request<PointsSummary>({
    url: getUrl('/points/summary'),
  });
}

export function getPointsRecords() {
  return request<PointsRecord[]>({
    url: getUrl('/points/records'),
  });
}
