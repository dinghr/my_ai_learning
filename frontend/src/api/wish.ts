import { request } from './request';
import { getStudentId } from '../utils/auth';

export interface Wish {
  id: string;
  name: string;
  icon: string;
  description?: string;
  points_required: number;
  points_progress: number;
  status: string;
  is_featured: boolean;
}

function getUrl(path: string) {
  return `/students/${getStudentId() || 'demo-student'}${path}`;
}

export function getWishes() {
  return request<Wish[]>({
    url: getUrl('/wishes'),
  });
}

export function getFeaturedWish() {
  return request<Wish | null>({
    url: getUrl('/wishes/featured'),
  });
}

export function createWish(wish: { name: string; icon: string; points_required: number; description?: string }) {
  return request<Wish>({
    url: getUrl('/wishes'),
    method: 'POST',
    data: wish,
  });
}

export function addWishProgress(wishId: string, points: number) {
  return request<Wish>({
    url: getUrl(`/wishes/${wishId}/progress`),
    method: 'POST',
    data: { points },
  });
}

export function completeWish(wishId: string) {
  return request({
    url: getUrl(`/wishes/${wishId}/complete`),
    method: 'POST',
  });
}
