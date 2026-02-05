from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Planet(Base):
    __tablename__ = "planets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    # z = Column(Integer, nullable=False) # 2D for now as per requirements

    slots = Column(Integer, default=5, nullable=False)
    temperature = Column(Integer, nullable=False) # Celsius? Kelvin? Just a value for now.
    gravity = Column(Integer, default=1000, nullable=False) # Relative to Earth (1.0 -> 1000)

    owner_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", backref="planets")
