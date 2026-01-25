from sqlalchemy.ext.asyncio import AsyncSession

from app.services import BoardService
from app.schemas import CardResponse, CardGroupResponse
from app.websocket.manager import ConnectionManager


class WebSocketHandler:
    def __init__(self, db: AsyncSession, manager: ConnectionManager, board_slug: str, session_id: str):
        self.db = db
        self.manager = manager
        self.board_slug = board_slug
        self.session_id = session_id
        self.service = BoardService(db)

    async def handle_message(self, data: dict) -> dict | None:
        event_type = data.get("type", "")
        payload = data.get("payload", {})

        handlers = {
            "card:create": self.handle_card_create,
            "card:update": self.handle_card_update,
            "card:move": self.handle_card_move,
            "card:delete": self.handle_card_delete,
            "vote:toggle": self.handle_vote_toggle,
            "group:create": self.handle_group_create,
            "group:update": self.handle_group_update,
            "group:dissolve": self.handle_group_dissolve,
            "timer:start": self.handle_timer_start,
            "timer:stop": self.handle_timer_stop,
            "timer:reset": self.handle_timer_reset,
        }

        handler = handlers.get(event_type)
        if handler:
            return await handler(payload)
        return None

    async def handle_card_create(self, payload: dict) -> dict:
        column_id = payload.get("column_id")
        content = payload.get("content", "")
        color = payload.get("color", "#fef08a")

        card = await self.service.create_card(column_id, content, color, self.session_id)
        card_data = CardResponse.from_orm_with_votes(card).model_dump(mode="json")

        await self.manager.broadcast(
            self.board_slug,
            {"type": "card:created", "payload": card_data},
            exclude_session=self.session_id,
        )
        return {"type": "card:created", "payload": card_data}

    async def handle_card_update(self, payload: dict) -> dict:
        card_id = payload.get("card_id")
        content = payload.get("content")
        color = payload.get("color")

        update_data = {}
        if content is not None:
            update_data["content"] = content
        if color is not None:
            update_data["color"] = color

        card = await self.service.update_card(card_id, **update_data)
        if card:
            card_data = CardResponse.from_orm_with_votes(card).model_dump(mode="json")
            await self.manager.broadcast(
                self.board_slug,
                {"type": "card:updated", "payload": card_data},
                exclude_session=self.session_id,
            )
            return {"type": "card:updated", "payload": card_data}
        return {"type": "error", "payload": {"message": "Card not found"}}

    async def handle_card_move(self, payload: dict) -> dict:
        card_id = payload.get("card_id")
        column_id = payload.get("column_id")
        position = payload.get("position")
        group_id = payload.get("group_id")

        card = await self.service.move_card(card_id, column_id, position, group_id)
        if card:
            card_data = CardResponse.from_orm_with_votes(card).model_dump(mode="json")
            await self.manager.broadcast(
                self.board_slug,
                {"type": "card:moved", "payload": card_data},
                exclude_session=self.session_id,
            )
            return {"type": "card:moved", "payload": card_data}
        return {"type": "error", "payload": {"message": "Card not found"}}

    async def handle_card_delete(self, payload: dict) -> dict:
        card_id = payload.get("card_id")
        success = await self.service.delete_card(card_id)
        if success:
            await self.manager.broadcast(
                self.board_slug,
                {"type": "card:deleted", "payload": {"card_id": card_id}},
                exclude_session=self.session_id,
            )
            return {"type": "card:deleted", "payload": {"card_id": card_id}}
        return {"type": "error", "payload": {"message": "Card not found"}}

    async def handle_vote_toggle(self, payload: dict) -> dict:
        card_id = payload.get("card_id")
        result = await self.service.toggle_vote(card_id, self.session_id, self.board_slug)

        if result["success"]:
            card = await self.service.get_card_with_votes(card_id)
            vote_data = {
                "card_id": card_id,
                "vote_count": len(card.votes) if card else 0,
                "session_id": self.session_id,
                "voted": result["voted"],
            }
            await self.manager.broadcast_all(
                self.board_slug,
                {"type": "vote:changed", "payload": vote_data},
            )
            return {"type": "vote:changed", "payload": vote_data}
        return {"type": "error", "payload": {"message": result.get("error", "Vote failed")}}

    async def handle_group_create(self, payload: dict) -> dict:
        column_id = payload.get("column_id")
        title = payload.get("title", "")
        card_ids = payload.get("card_ids", [])

        board = await self.service.get_board_by_slug(self.board_slug)
        if not board:
            return {"type": "error", "payload": {"message": "Board not found"}}

        group = await self.service.create_group(board.id, column_id, title)

        # Move cards to group
        for card_id in card_ids:
            await self.service.update_card(card_id, group_id=group.id)

        group_data = CardGroupResponse.model_validate(group).model_dump(mode="json")
        await self.manager.broadcast(
            self.board_slug,
            {"type": "group:created", "payload": {"group": group_data, "card_ids": card_ids}},
            exclude_session=self.session_id,
        )
        return {"type": "group:created", "payload": {"group": group_data, "card_ids": card_ids}}

    async def handle_group_update(self, payload: dict) -> dict:
        group_id = payload.get("group_id")
        title = payload.get("title")

        group = await self.service.update_group(group_id, title=title)
        if group:
            group_data = CardGroupResponse.model_validate(group).model_dump(mode="json")
            await self.manager.broadcast(
                self.board_slug,
                {"type": "group:updated", "payload": group_data},
                exclude_session=self.session_id,
            )
            return {"type": "group:updated", "payload": group_data}
        return {"type": "error", "payload": {"message": "Group not found"}}

    async def handle_group_dissolve(self, payload: dict) -> dict:
        group_id = payload.get("group_id")
        success = await self.service.dissolve_group(group_id)
        if success:
            await self.manager.broadcast(
                self.board_slug,
                {"type": "group:dissolved", "payload": {"group_id": group_id}},
                exclude_session=self.session_id,
            )
            return {"type": "group:dissolved", "payload": {"group_id": group_id}}
        return {"type": "error", "payload": {"message": "Group not found"}}

    async def handle_timer_start(self, payload: dict) -> dict:
        board = await self.service.start_timer(self.board_slug)
        if board:
            timer_data = {
                "timer_end_time": board.timer_end_time.isoformat() + "Z" if board.timer_end_time else None,
                "timer_duration": board.timer_duration,
            }
            await self.manager.broadcast_all(
                self.board_slug,
                {"type": "timer:started", "payload": timer_data},
            )
            return {"type": "timer:started", "payload": timer_data}
        return {"type": "error", "payload": {"message": "Board not found"}}

    async def handle_timer_stop(self, payload: dict) -> dict:
        board = await self.service.stop_timer(self.board_slug)
        if board:
            await self.manager.broadcast_all(
                self.board_slug,
                {"type": "timer:stopped", "payload": {}},
            )
            return {"type": "timer:stopped", "payload": {}}
        return {"type": "error", "payload": {"message": "Board not found"}}

    async def handle_timer_reset(self, payload: dict) -> dict:
        board = await self.service.reset_timer(self.board_slug)
        if board:
            await self.manager.broadcast_all(
                self.board_slug,
                {"type": "timer:reset", "payload": {"timer_duration": board.timer_duration}},
            )
            return {"type": "timer:reset", "payload": {"timer_duration": board.timer_duration}}
        return {"type": "error", "payload": {"message": "Board not found"}}
