import json
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, board_slug: str, session_id: str):
        await websocket.accept()
        if board_slug not in self.active_connections:
            self.active_connections[board_slug] = {}
        self.active_connections[board_slug][session_id] = websocket

    def disconnect(self, board_slug: str, session_id: str):
        if board_slug in self.active_connections:
            self.active_connections[board_slug].pop(session_id, None)
            if not self.active_connections[board_slug]:
                del self.active_connections[board_slug]

    async def send_personal(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, board_slug: str, message: dict, exclude_session: str | None = None):
        if board_slug in self.active_connections:
            for session_id, connection in self.active_connections[board_slug].items():
                if session_id != exclude_session:
                    try:
                        await connection.send_json(message)
                    except Exception:
                        pass

    async def broadcast_all(self, board_slug: str, message: dict):
        await self.broadcast(board_slug, message, exclude_session=None)

    def get_connected_users(self, board_slug: str) -> list[str]:
        if board_slug in self.active_connections:
            return list(self.active_connections[board_slug].keys())
        return []
