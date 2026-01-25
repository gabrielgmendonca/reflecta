from datetime import datetime
from pydantic import BaseModel

from app.schemas.vote import VoteResponse


class CardCreate(BaseModel):
    content: str
    color: str = "#fef08a"
    session_id: str


class CardUpdate(BaseModel):
    content: str | None = None
    color: str | None = None


class CardMove(BaseModel):
    column_id: int
    position: int
    group_id: int | None = None


class CardResponse(BaseModel):
    id: int
    column_id: int
    group_id: int | None
    content: str
    color: str
    position: int
    session_id: str
    created_at: datetime
    votes: list[VoteResponse] = []
    vote_count: int = 0

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_votes(cls, card):
        return cls(
            id=card.id,
            column_id=card.column_id,
            group_id=card.group_id,
            content=card.content,
            color=card.color,
            position=card.position,
            session_id=card.session_id,
            created_at=card.created_at,
            votes=[VoteResponse.model_validate(v) for v in card.votes],
            vote_count=len(card.votes),
        )
