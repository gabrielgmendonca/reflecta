from sqlalchemy import Column as Col, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class CardGroup(Base):
    __tablename__ = "card_groups"

    id = Col(Integer, primary_key=True, index=True)
    board_id = Col(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    column_id = Col(Integer, ForeignKey("columns.id", ondelete="CASCADE"), nullable=False)
    title = Col(String(100), default="")
    position = Col(Integer, default=0)

    board = relationship("Board", back_populates="groups")
    column = relationship("Column", back_populates="groups")
    cards = relationship("Card", back_populates="group", order_by="Card.position")
