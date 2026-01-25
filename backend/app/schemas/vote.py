from datetime import datetime
from pydantic import BaseModel


class VoteResponse(BaseModel):
    id: int
    card_id: int
    session_id: str
    created_at: datetime

    class Config:
        from_attributes = True
