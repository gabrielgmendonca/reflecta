from datetime import datetime
from sqlalchemy import Column as Col, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Vote(Base):
    __tablename__ = "votes"

    id = Col(Integer, primary_key=True, index=True)
    card_id = Col(Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)
    session_id = Col(String(50), nullable=False)
    created_at = Col(DateTime, default=datetime.utcnow)

    card = relationship("Card", back_populates="votes")

    __table_args__ = (
        UniqueConstraint("card_id", "session_id", name="unique_vote_per_session"),
    )
