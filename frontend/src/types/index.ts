export interface Board {
  id: number;
  slug: string;
  title: string;
  owner_id: number | null;
  timer_duration: number;
  timer_end_time: string | null;
  allow_voting: boolean;
  max_votes_per_user: number;
  created_at: string;
  columns: Column[];
}

export interface Column {
  id: number;
  board_id: number;
  title: string;
  color: string;
  position: number;
  cards: Card[];
  groups: CardGroup[];
}

export interface Card {
  id: number;
  column_id: number;
  group_id: number | null;
  content: string;
  color: string;
  position: number;
  session_id: string;
  created_at: string;
  votes: Vote[];
  vote_count: number;
}

export interface Vote {
  id: number;
  card_id: number;
  session_id: string;
  created_at: string;
}

export interface CardGroup {
  id: number;
  board_id: number;
  column_id: number;
  title: string;
  position: number;
}

export interface Template {
  id: number;
  name: string;
  description: string;
  columns: { title: string; color: string }[];
}

export interface WebSocketMessage {
  type: string;
  payload: Record<string, unknown>;
}

export interface User {
  id: number;
  email: string;
  name: string;
  picture: string | null;
}
