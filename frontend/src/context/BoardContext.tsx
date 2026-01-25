import { createContext, useContext, useEffect, useCallback, type ReactNode } from 'react';
import { create } from 'zustand';
import type { Board, Card, CardGroup, WebSocketMessage } from '../types';
import { api } from '../api/client';
import { useWebSocket } from '../hooks/useWebSocket';
import { useSessionId } from '../hooks/useSessionId';

interface BoardState {
  board: Board | null;
  loading: boolean;
  error: string | null;
  setBoard: (board: Board | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  updateCard: (card: Card) => void;
  removeCard: (cardId: number) => void;
  addCard: (card: Card) => void;
  replaceOptimisticCard: (tempId: number, realCard: Card) => void;
  updateVoteCount: (cardId: number, voteCount: number, votes: Card['votes']) => void;
  updateTimerEndTime: (endTime: string | null) => void;
  addGroup: (group: CardGroup, cardIds: number[]) => void;
  removeGroup: (groupId: number) => void;
}

const useBoardStore = create<BoardState>((set) => ({
  board: null,
  loading: false,
  error: null,
  setBoard: (board) => set({ board }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  updateCard: (updatedCard) =>
    set((state) => {
      if (!state.board) return state;
      return {
        board: {
          ...state.board,
          columns: state.board.columns.map((col) => ({
            ...col,
            cards: col.cards.map((card) =>
              card.id === updatedCard.id ? updatedCard : card
            ),
          })),
        },
      };
    }),
  removeCard: (cardId) =>
    set((state) => {
      if (!state.board) return state;
      return {
        board: {
          ...state.board,
          columns: state.board.columns.map((col) => ({
            ...col,
            cards: col.cards.filter((card) => card.id !== cardId),
          })),
        },
      };
    }),
  addCard: (newCard) =>
    set((state) => {
      if (!state.board) return state;
      // Check if card already exists (optimistic update case)
      const cardExists = state.board.columns.some((col) =>
        col.cards.some((card) => card.id === newCard.id)
      );
      if (cardExists) return state;
      return {
        board: {
          ...state.board,
          columns: state.board.columns.map((col) =>
            col.id === newCard.column_id
              ? { ...col, cards: [...col.cards, newCard] }
              : col
          ),
        },
      };
    }),
  replaceOptimisticCard: (tempId: number, realCard: Card) =>
    set((state) => {
      if (!state.board) return state;
      return {
        board: {
          ...state.board,
          columns: state.board.columns.map((col) => ({
            ...col,
            cards: col.cards.map((card) =>
              card.id === tempId ? realCard : card
            ),
          })),
        },
      };
    }),
  updateVoteCount: (cardId, voteCount, votes) =>
    set((state) => {
      if (!state.board) return state;
      return {
        board: {
          ...state.board,
          columns: state.board.columns.map((col) => ({
            ...col,
            cards: col.cards.map((card) =>
              card.id === cardId ? { ...card, vote_count: voteCount, votes } : card
            ),
          })),
        },
      };
    }),
  updateTimerEndTime: (endTime) =>
    set((state) => {
      if (!state.board) return state;
      return {
        board: { ...state.board, timer_end_time: endTime },
      };
    }),
  addGroup: (group, cardIds) =>
    set((state) => {
      if (!state.board) return state;
      return {
        board: {
          ...state.board,
          columns: state.board.columns.map((col) =>
            col.id === group.column_id
              ? {
                  ...col,
                  groups: [...col.groups, group],
                  cards: col.cards.map((card) =>
                    cardIds.includes(card.id) ? { ...card, group_id: group.id } : card
                  ),
                }
              : col
          ),
        },
      };
    }),
  removeGroup: (groupId) =>
    set((state) => {
      if (!state.board) return state;
      return {
        board: {
          ...state.board,
          columns: state.board.columns.map((col) => ({
            ...col,
            groups: col.groups.filter((g) => g.id !== groupId),
            cards: col.cards.map((card) =>
              card.group_id === groupId ? { ...card, group_id: null } : card
            ),
          })),
        },
      };
    }),
}));

interface BoardContextValue {
  board: Board | null;
  loading: boolean;
  error: string | null;
  sessionId: string;
  isConnected: boolean;
  loadBoard: (slug: string) => Promise<void>;
  createCard: (columnId: number, content: string, color?: string) => Promise<void>;
  updateCard: (cardId: number, data: { content?: string; color?: string }) => Promise<void>;
  moveCard: (cardId: number, columnId: number, position: number, groupId?: number) => void;
  deleteCard: (cardId: number) => Promise<void>;
  toggleVote: (cardId: number) => Promise<void>;
  createGroup: (columnId: number, cardIds: number[], title?: string) => Promise<void>;
  dissolveGroup: (groupId: number) => Promise<void>;
  startTimer: () => Promise<void>;
  stopTimer: () => Promise<void>;
  resetTimer: () => Promise<void>;
}

const BoardContext = createContext<BoardContextValue | null>(null);

export function BoardProvider({ children, slug }: { children: ReactNode; slug: string }) {
  const sessionId = useSessionId();
  const store = useBoardStore();
  const { send, subscribe, isConnected } = useWebSocket(slug, sessionId);

  const loadBoard = useCallback(async (boardSlug: string) => {
    store.setLoading(true);
    store.setError(null);
    try {
      const board = await api.getBoard(boardSlug);
      store.setBoard(board);
    } catch (err) {
      store.setError(err instanceof Error ? err.message : 'Failed to load board');
    } finally {
      store.setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (slug) {
      loadBoard(slug);
    }
    return () => {
      store.setBoard(null);
    };
  }, [slug, loadBoard]);

  useEffect(() => {
    const unsubscribe = subscribe((message: WebSocketMessage) => {
      const { type, payload } = message;

      switch (type) {
        case 'card:created':
          {
            const newCard = payload as unknown as Card;
            // Check if there's an optimistic card to replace (negative ID, same content, same column)
            const optimisticCard = store.board?.columns
              .find((c) => c.id === newCard.column_id)
              ?.cards.find(
                (card) =>
                  card.id < 0 &&
                  card.content === newCard.content &&
                  card.session_id === newCard.session_id
              );
            if (optimisticCard) {
              store.replaceOptimisticCard(optimisticCard.id, newCard);
            } else {
              store.addCard(newCard);
            }
          }
          break;
        case 'card:updated':
        case 'card:moved':
          // For moved cards, we need to refresh the board to get correct positions
          if (type === 'card:moved') {
            loadBoard(slug);
          } else {
            store.updateCard(payload as unknown as Card);
          }
          break;
        case 'card:deleted':
          store.removeCard((payload as { card_id: number }).card_id);
          break;
        case 'vote:changed':
          // Reload to get full vote data
          loadBoard(slug);
          break;
        case 'timer:started':
          {
            const { timer_end_time } = payload as { timer_end_time: string };
            store.updateTimerEndTime(timer_end_time);
          }
          break;
        case 'timer:stopped':
        case 'timer:reset':
          store.updateTimerEndTime(null);
          break;
        case 'group:created':
          {
            const { group, card_ids } = payload as { group: CardGroup; card_ids: number[] };
            store.addGroup(group, card_ids);
          }
          break;
        case 'group:dissolved':
          {
            const { group_id } = payload as { group_id: number };
            store.removeGroup(group_id);
          }
          break;
      }
    });

    return unsubscribe;
  }, [subscribe, slug, loadBoard]);

  const createCard = useCallback(
    async (columnId: number, content: string, color?: string) => {
      // Optimistic update: add card immediately with a temporary negative ID
      const tempId = -Date.now();
      const column = store.board?.columns.find((c) => c.id === columnId);
      const optimisticCard: Card = {
        id: tempId,
        content,
        color: color || '#ffffff',
        column_id: columnId,
        position: column?.cards.length ?? 0,
        vote_count: 0,
        votes: [],
        group_id: null,
        session_id: sessionId,
        created_at: new Date().toISOString(),
      };
      store.addCard(optimisticCard);
      send('card:create', { column_id: columnId, content, color, temp_id: tempId });
    },
    [send, sessionId, store.board]
  );

  const updateCard = useCallback(
    async (cardId: number, data: { content?: string; color?: string }) => {
      send('card:update', { card_id: cardId, ...data });
    },
    [send]
  );

  const moveCard = useCallback(
    (cardId: number, columnId: number, position: number, groupId?: number) => {
      send('card:move', { card_id: cardId, column_id: columnId, position, group_id: groupId });
    },
    [send]
  );

  const deleteCard = useCallback(
    async (cardId: number) => {
      send('card:delete', { card_id: cardId });
    },
    [send]
  );

  const toggleVote = useCallback(
    async (cardId: number) => {
      send('vote:toggle', { card_id: cardId });
    },
    [send]
  );

  const createGroup = useCallback(
    async (columnId: number, cardIds: number[], title?: string) => {
      send('group:create', { column_id: columnId, card_ids: cardIds, title: title || '' });
    },
    [send]
  );

  const dissolveGroup = useCallback(
    async (groupId: number) => {
      send('group:dissolve', { group_id: groupId });
    },
    [send]
  );

  const startTimer = useCallback(async () => {
    send('timer:start', {});
  }, [send]);

  const stopTimer = useCallback(async () => {
    send('timer:stop', {});
  }, [send]);

  const resetTimer = useCallback(async () => {
    send('timer:reset', {});
  }, [send]);

  return (
    <BoardContext.Provider
      value={{
        board: store.board,
        loading: store.loading,
        error: store.error,
        sessionId,
        isConnected,
        loadBoard,
        createCard,
        updateCard,
        moveCard,
        deleteCard,
        toggleVote,
        createGroup,
        dissolveGroup,
        startTimer,
        stopTimer,
        resetTimer,
      }}
    >
      {children}
    </BoardContext.Provider>
  );
}

export function useBoard() {
  const context = useContext(BoardContext);
  if (!context) {
    throw new Error('useBoard must be used within a BoardProvider');
  }
  return context;
}
