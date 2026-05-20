import { request } from './request';
import { getStudentId } from '../utils/auth';

export interface ChatMessage {
  id: string;
  student_id: string;
  role: 'user' | 'assistant';
  content: string;
  content_type: string;
  intent?: string;
  intent_confidence?: number;
  image_url?: string;
  session_id: string;
  created_at: string;
  meta?: Record<string, any>;
}

export interface ChatResponse {
  message: ChatMessage;
  intent?: string;
  suggestions?: string[];
}

export interface QuickReply {
  label: string;
  icon: string;
  prompt: string;
}

function getUrl(path: string) {
  return `/students/${getStudentId() || 'demo-student'}${path}`;
}

export function sendChatMessage(message: string, sessionId?: string, imageUrl?: string) {
  return request<ChatResponse>({
    url: getUrl('/ai-chat/chat'),
    method: 'POST',
    data: { message, session_id: sessionId, image_url: imageUrl },
  });
}

export function getQuickReplies(intent?: string) {
  const params = intent ? `?intent=${intent}` : '';
  return request<QuickReply[]>({
    url: getUrl(`/ai-chat/quick-replies${params}`),
  });
}

export function getChatHistory(sessionId: string) {
  return request<ChatMessage[]>({
    url: getUrl(`/ai-chat/sessions/${sessionId}/messages`),
  });
}
