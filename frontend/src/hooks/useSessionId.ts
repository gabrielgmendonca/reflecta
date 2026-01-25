import { useState } from 'react';

function generateSessionId(): string {
  return 'session_' + Math.random().toString(36).substring(2, 15);
}

export function useSessionId(): string {
  const [sessionId] = useState(() => {
    const stored = localStorage.getItem('retro-session-id');
    if (stored) return stored;
    const newId = generateSessionId();
    localStorage.setItem('retro-session-id', newId);
    return newId;
  });

  return sessionId;
}
