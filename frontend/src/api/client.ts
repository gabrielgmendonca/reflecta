import type { Board, Template } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function fetchJSON<T>(url: string, options?: RequestInit & { token?: string }): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options?.headers as Record<string, string>,
  };

  if (options?.token) {
    headers['Authorization'] = `Bearer ${options.token}`;
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }
  return response.json();
}

export const api = {
  // Boards
  createBoard: (title: string, templateId?: number, token?: string) =>
    fetchJSON<Board>('/boards', {
      method: 'POST',
      body: JSON.stringify({ title, template_id: templateId }),
      token,
    }),

  getMyBoards: (token: string) =>
    fetchJSON<Board[]>('/boards/my', { token }),

  getBoard: (slug: string) => fetchJSON<Board>(`/boards/${slug}`),

  deleteBoard: (slug: string, token: string) =>
    fetchJSON(`/boards/${slug}`, { method: 'DELETE', token }),

  updateBoard: (slug: string, data: Partial<Board>) =>
    fetchJSON<Board>(`/boards/${slug}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  // Columns
  createColumn: (slug: string, title: string, color: string) =>
    fetchJSON(`/boards/${slug}/columns`, {
      method: 'POST',
      body: JSON.stringify({ title, color }),
    }),

  updateColumn: (slug: string, columnId: number, data: { title?: string; color?: string }) =>
    fetchJSON(`/boards/${slug}/columns/${columnId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteColumn: (slug: string, columnId: number) =>
    fetchJSON(`/boards/${slug}/columns/${columnId}`, { method: 'DELETE' }),

  // Cards
  createCard: (slug: string, columnId: number, content: string, sessionId: string, color?: string) =>
    fetchJSON(`/boards/${slug}/columns/${columnId}/cards`, {
      method: 'POST',
      body: JSON.stringify({ content, session_id: sessionId, color }),
    }),

  updateCard: (slug: string, cardId: number, data: { content?: string; color?: string }) =>
    fetchJSON(`/boards/${slug}/cards/${cardId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  moveCard: (slug: string, cardId: number, columnId: number, position: number, groupId?: number) =>
    fetchJSON(`/boards/${slug}/cards/${cardId}/move`, {
      method: 'PUT',
      body: JSON.stringify({ column_id: columnId, position, group_id: groupId }),
    }),

  deleteCard: (slug: string, cardId: number) =>
    fetchJSON(`/boards/${slug}/cards/${cardId}`, { method: 'DELETE' }),

  // Voting
  toggleVote: (slug: string, cardId: number, sessionId: string) =>
    fetchJSON(`/boards/${slug}/cards/${cardId}/vote?session_id=${sessionId}`, {
      method: 'POST',
    }),

  // Groups
  createGroup: (slug: string, columnId: number, title?: string) =>
    fetchJSON(`/boards/${slug}/groups`, {
      method: 'POST',
      body: JSON.stringify({ column_id: columnId, title: title || '' }),
    }),

  updateGroup: (slug: string, groupId: number, title: string) =>
    fetchJSON(`/boards/${slug}/groups/${groupId}`, {
      method: 'PATCH',
      body: JSON.stringify({ title }),
    }),

  dissolveGroup: (slug: string, groupId: number) =>
    fetchJSON(`/boards/${slug}/groups/${groupId}`, { method: 'DELETE' }),

  // Timer
  startTimer: (slug: string) =>
    fetchJSON<Board>(`/boards/${slug}/timer/start`, { method: 'POST' }),

  stopTimer: (slug: string) =>
    fetchJSON<Board>(`/boards/${slug}/timer/stop`, { method: 'POST' }),

  resetTimer: (slug: string) =>
    fetchJSON<Board>(`/boards/${slug}/timer/reset`, { method: 'POST' }),

  // Export
  exportJSON: (slug: string) => `${API_BASE}/boards/${slug}/export/json`,
  exportCSV: (slug: string) => `${API_BASE}/boards/${slug}/export/csv`,
  exportPDF: (slug: string) => `${API_BASE}/boards/${slug}/export/pdf`,

  // Templates
  getTemplates: () => fetchJSON<Template[]>('/templates'),
};
