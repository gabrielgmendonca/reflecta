from pydantic import BaseModel


class CardGroupCreate(BaseModel):
    column_id: int
    title: str = ""


class CardGroupUpdate(BaseModel):
    title: str | None = None
    position: int | None = None


class CardGroupResponse(BaseModel):
    id: int
    board_id: int
    column_id: int
    title: str
    position: int

    class Config:
        from_attributes = True
