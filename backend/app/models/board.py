from datetime import datetime
from sqlalchemy import Column as Col, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Board(Base):
    __tablename__ = "boards"

    id = Col(Integer, primary_key=True, index=True)
    slug = Col(String(50), unique=True, index=True, nullable=False)
    title = Col(String(200), nullable=False)
    owner_id = Col(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    timer_duration = Col(Integer, default=300)  # seconds
    timer_end_time = Col(DateTime, nullable=True)
    allow_voting = Col(Boolean, default=True)
    max_votes_per_user = Col(Integer, default=5)
    created_at = Col(DateTime, default=datetime.utcnow)
    updated_at = Col(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="boards")
    columns = relationship("Column", back_populates="board", cascade="all, delete-orphan", order_by="Column.position")
    groups = relationship("CardGroup", back_populates="board", cascade="all, delete-orphan")
