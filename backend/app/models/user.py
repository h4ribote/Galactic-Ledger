from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.sql import func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=False)
    username = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
