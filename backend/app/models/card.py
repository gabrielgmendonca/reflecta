from datetime import datetime
from sqlalchemy import Column as Col, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Card(Base):
    __tablename__ = "cards"

    id = Col(Integer, primary_key=True, index=True)
    column_id = Col(Integer, ForeignKey("columns.id", ondelete="CASCADE"), nullable=False)
    group_id = Col(Integer, ForeignKey("card_groups.id", ondelete="SET NULL"), nullable=True)
    content = Col(Text, nullable=False)
    color = Col(String(20), default="#fef08a")
    position = Col(Integer, default=0)
    session_id = Col(String(50), nullable=False)
    created_at = Col(DateTime, default=datetime.utcnow)

    column = relationship("Column", back_populates="cards")
    group = relationship("CardGroup", back_populates="cards")
    votes = relationship("Vote", back_populates="card", cascade="all, delete-orphan")
