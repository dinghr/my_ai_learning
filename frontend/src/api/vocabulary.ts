import { request } from './request';
import { getStudentId } from '../utils/auth';

export interface Character {
  id: string;
  character: string;
  pinyin?: string;
  radical?: string;
  words: string[];
  example?: string;
  brainstorm: string[];
  status: string;
  review_count: number;
  correct_count: number;
  wrong_count: number;
  group_id: number;
  review_round: number;
  last_reviewed_at?: string;
  next_review_at?: string;
  created_at: string;
}

export interface QuizGroup {
  group_id: number;
  characters: Character[];
  total: number;
}

export interface ReviewResult {
  character_id: string;
  result: 'know' | 'unknow' | 'study';
  group_id: number;
  review_round: number;
}

export interface ReadingPassage {
  title: string;
  author?: string;
  content: { hz: string; py: string; highlight?: boolean }[];
  summary: string;
  highlight_words?: string[];
}

const studentId = getStudentId() || 'demo-student';

export async function addCharacter(character: string) {
  return request<Character>({
    url: `/students/${studentId}/literacy/characters`,
    method: 'POST',
    data: { character },
  });
}

export async function addCharactersBatch(characters: string[]) {
  return request<Character[]>({
    url: `/students/${studentId}/literacy/characters/batch`,
    method: 'POST',
    data: { characters },
  });
}

export async function getCharacters(status?: string) {
  return request<Character[]>({
    url: `/students/${studentId}/literacy/characters`,
    method: 'GET',
    data: status ? { status } : undefined,
  });
}

export async function getQuizGroup() {
  return request<QuizGroup>({
    url: `/students/${studentId}/literacy/quiz`,
    method: 'GET',
  });
}

export async function submitQuizResults(results: ReviewResult[]) {
  return request<Character[]>({
    url: `/students/${studentId}/literacy/quiz/submit`,
    method: 'POST',
    data: { results },
  });
}

export async function generateReading(theme?: string) {
  return request<ReadingPassage>({
    url: `/students/${studentId}/literacy/reading`,
    method: 'POST',
    data: { theme },
  });
}
