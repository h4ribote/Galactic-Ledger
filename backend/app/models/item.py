from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    tier = Column(Integer, default=1, nullable=False)
    volume = Column(Integer, default=1000, nullable=False)
