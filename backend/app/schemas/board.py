from datetime import datetime
from pydantic import BaseModel, field_serializer

from app.schemas.column import ColumnResponse


class BoardCreate(BaseModel):
    title: str
    template_id: int | None = None


class BoardUpdate(BaseModel):
    title: str | None = None
    timer_duration: int | None = None
    allow_voting: bool | None = None
    max_votes_per_user: int | None = None


class BoardResponse(BaseModel):
    id: int
    slug: str
    title: str
    owner_id: int | None
    timer_duration: int
    timer_end_time: datetime | None
    allow_voting: bool
    max_votes_per_user: int
    created_at: datetime

    class Config:
        from_attributes = True

    @field_serializer("timer_end_time", "created_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat() + "Z"


class BoardFullResponse(BoardResponse):
    columns: list[ColumnResponse]

    class Config:
        from_attributes = True
