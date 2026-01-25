from datetime import datetime, timedelta
import shortuuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Board, Column, Card, Vote, CardGroup, Template


class BoardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_board(self, title: str, template_id: int | None = None, owner_id: int | None = None) -> Board:
        slug = shortuuid.uuid()[:8].lower()
        board = Board(title=title, slug=slug, owner_id=owner_id)
        self.db.add(board)
        await self.db.flush()

        if template_id:
            template = await self.db.get(Template, template_id)
            if template and template.columns:
                for i, col_data in enumerate(template.columns):
                    column = Column(
                        board_id=board.id,
                        title=col_data["title"],
                        color=col_data["color"],
                        position=i,
                    )
                    self.db.add(column)
        else:
            # Default columns
            default_columns = [
                {"title": "Start", "color": "#22c55e"},
                {"title": "Stop", "color": "#ef4444"},
                {"title": "Continue", "color": "#3b82f6"},
            ]
            for i, col_data in enumerate(default_columns):
                column = Column(
                    board_id=board.id,
                    title=col_data["title"],
                    color=col_data["color"],
                    position=i,
                )
                self.db.add(column)

        await self.db.commit()
        return await self.get_board_by_slug(board.slug)

    async def get_board_by_slug(self, slug: str) -> Board | None:
        stmt = (
            select(Board)
            .where(Board.slug == slug)
            .options(
                selectinload(Board.columns).selectinload(Column.cards).selectinload(Card.votes),
                selectinload(Board.columns).selectinload(Column.groups),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_boards_by_owner(self, owner_id: int) -> list[Board]:
        stmt = (
            select(Board)
            .where(Board.owner_id == owner_id)
            .order_by(Board.updated_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_board(self, slug: str, **kwargs) -> Board | None:
        board = await self.get_board_by_slug(slug)
        if not board:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(board, key, value)
        await self.db.commit()
        return board

    async def delete_board(self, slug: str) -> bool:
        stmt = select(Board).where(Board.slug == slug)
        result = await self.db.execute(stmt)
        board = result.scalar_one_or_none()
        if not board:
            return False
        await self.db.delete(board)
        await self.db.commit()
        return True

    async def create_column(self, board_id: int, title: str, color: str, position: int | None = None) -> Column:
        if position is None:
            stmt = select(Column).where(Column.board_id == board_id)
            result = await self.db.execute(stmt)
            columns = result.scalars().all()
            position = len(columns)

        column = Column(board_id=board_id, title=title, color=color, position=position)
        self.db.add(column)
        await self.db.commit()
        await self.db.refresh(column)
        return column

    async def update_column(self, column_id: int, **kwargs) -> Column | None:
        column = await self.db.get(Column, column_id)
        if not column:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(column, key, value)
        await self.db.commit()
        await self.db.refresh(column)
        return column

    async def delete_column(self, column_id: int) -> bool:
        column = await self.db.get(Column, column_id)
        if not column:
            return False
        await self.db.delete(column)
        await self.db.commit()
        return True

    async def create_card(self, column_id: int, content: str, color: str, session_id: str) -> Card:
        stmt = select(Card).where(Card.column_id == column_id)
        result = await self.db.execute(stmt)
        cards = result.scalars().all()
        position = len(cards)

        card = Card(column_id=column_id, content=content, color=color, session_id=session_id, position=position)
        self.db.add(card)
        await self.db.commit()

        stmt = select(Card).where(Card.id == card.id).options(selectinload(Card.votes))
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def update_card(self, card_id: int, **kwargs) -> Card | None:
        stmt = select(Card).where(Card.id == card_id).options(selectinload(Card.votes))
        result = await self.db.execute(stmt)
        card = result.scalar_one_or_none()
        if not card:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(card, key, value)
        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def move_card(self, card_id: int, column_id: int, position: int, group_id: int | None = None) -> Card | None:
        stmt = select(Card).where(Card.id == card_id).options(selectinload(Card.votes))
        result = await self.db.execute(stmt)
        card = result.scalar_one_or_none()
        if not card:
            return None

        old_column_id = card.column_id
        old_position = card.position

        # Update positions in old column
        if old_column_id == column_id:
            if position > old_position:
                stmt = select(Card).where(
                    Card.column_id == column_id,
                    Card.position > old_position,
                    Card.position <= position,
                    Card.id != card_id,
                )
                result = await self.db.execute(stmt)
                for c in result.scalars().all():
                    c.position -= 1
            else:
                stmt = select(Card).where(
                    Card.column_id == column_id,
                    Card.position >= position,
                    Card.position < old_position,
                    Card.id != card_id,
                )
                result = await self.db.execute(stmt)
                for c in result.scalars().all():
                    c.position += 1
        else:
            # Decrement positions in old column
            stmt = select(Card).where(Card.column_id == old_column_id, Card.position > old_position)
            result = await self.db.execute(stmt)
            for c in result.scalars().all():
                c.position -= 1

            # Increment positions in new column
            stmt = select(Card).where(Card.column_id == column_id, Card.position >= position)
            result = await self.db.execute(stmt)
            for c in result.scalars().all():
                c.position += 1

        card.column_id = column_id
        card.position = position
        card.group_id = group_id
        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def delete_card(self, card_id: int) -> bool:
        card = await self.db.get(Card, card_id)
        if not card:
            return False
        column_id = card.column_id
        position = card.position
        await self.db.delete(card)

        # Update positions
        stmt = select(Card).where(Card.column_id == column_id, Card.position > position)
        result = await self.db.execute(stmt)
        for c in result.scalars().all():
            c.position -= 1

        await self.db.commit()
        return True

    async def toggle_vote(self, card_id: int, session_id: str, board_slug: str) -> dict:
        # Check max votes
        board = await self.get_board_by_slug(board_slug)
        if not board or not board.allow_voting:
            return {"success": False, "error": "Voting not allowed"}

        # Count user's current votes on this board
        stmt = (
            select(Vote)
            .join(Card)
            .join(Column)
            .where(Column.board_id == board.id, Vote.session_id == session_id)
        )
        result = await self.db.execute(stmt)
        user_votes = result.scalars().all()

        # Check if already voted on this card
        existing_vote = next((v for v in user_votes if v.card_id == card_id), None)

        if existing_vote:
            await self.db.delete(existing_vote)
            await self.db.commit()
            # Expire cached objects to ensure fresh data on next fetch
            self.db.expire_all()
            return {"success": True, "voted": False}
        else:
            if len(user_votes) >= board.max_votes_per_user:
                return {"success": False, "error": "Max votes reached"}
            vote = Vote(card_id=card_id, session_id=session_id)
            self.db.add(vote)
            await self.db.commit()
            return {"success": True, "voted": True}

    async def create_group(self, board_id: int, column_id: int, title: str = "") -> CardGroup:
        stmt = select(CardGroup).where(CardGroup.column_id == column_id)
        result = await self.db.execute(stmt)
        groups = result.scalars().all()
        position = len(groups)

        group = CardGroup(board_id=board_id, column_id=column_id, title=title, position=position)
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def update_group(self, group_id: int, **kwargs) -> CardGroup | None:
        group = await self.db.get(CardGroup, group_id)
        if not group:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(group, key, value)
        await self.db.commit()
        await self.db.refresh(group)
        return group

    async def dissolve_group(self, group_id: int) -> bool:
        group = await self.db.get(CardGroup, group_id)
        if not group:
            return False

        # Ungroup all cards
        stmt = select(Card).where(Card.group_id == group_id)
        result = await self.db.execute(stmt)
        for card in result.scalars().all():
            card.group_id = None

        await self.db.delete(group)
        await self.db.commit()
        return True

    async def start_timer(self, slug: str) -> Board | None:
        board = await self.get_board_by_slug(slug)
        if not board:
            return None
        board.timer_end_time = datetime.utcnow() + timedelta(seconds=board.timer_duration)
        await self.db.commit()
        return board

    async def stop_timer(self, slug: str) -> Board | None:
        board = await self.get_board_by_slug(slug)
        if not board:
            return None
        board.timer_end_time = None
        await self.db.commit()
        return board

    async def reset_timer(self, slug: str) -> Board | None:
        board = await self.get_board_by_slug(slug)
        if not board:
            return None
        board.timer_end_time = None
        await self.db.commit()
        return board

    async def get_card_with_votes(self, card_id: int) -> Card | None:
        stmt = select(Card).where(Card.id == card_id).options(selectinload(Card.votes))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
