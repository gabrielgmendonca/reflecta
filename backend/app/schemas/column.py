from pydantic import BaseModel

from app.schemas.card import CardResponse
from app.schemas.card_group import CardGroupResponse


class ColumnCreate(BaseModel):
    title: str
    color: str = "#3b82f6"
    position: int | None = None


class ColumnUpdate(BaseModel):
    title: str | None = None
    color: str | None = None
    position: int | None = None


class ColumnResponse(BaseModel):
    id: int
    board_id: int
    title: str
    color: str
    position: int
    cards: list[CardResponse] = []
    groups: list[CardGroupResponse] = []

    class Config:
        from_attributes = True
