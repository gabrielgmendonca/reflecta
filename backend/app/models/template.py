from sqlalchemy import Column as Col, Integer, String, JSON

from app.database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Col(Integer, primary_key=True, index=True)
    name = Col(String(100), nullable=False)
    description = Col(String(500), default="")
    columns = Col(JSON, nullable=False)  # List of {title, color}
