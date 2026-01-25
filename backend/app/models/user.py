from datetime import datetime
from sqlalchemy import Column as Col, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Col(Integer, primary_key=True, index=True)
    email = Col(String(255), unique=True, index=True, nullable=False)
    name = Col(String(255), nullable=False)
    picture = Col(String(500), nullable=True)
    google_id = Col(String(255), unique=True, nullable=False)
    created_at = Col(DateTime, default=datetime.utcnow)
    last_login = Col(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    boards = relationship("Board", back_populates="owner", cascade="all, delete-orphan")
