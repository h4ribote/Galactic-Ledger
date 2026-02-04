from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Planet(Base):
    __tablename__ = "planets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    # z = Column(Float, nullable=False) # 2D for now as per requirements

    slots = Column(Integer, default=5, nullable=False)
    temperature = Column(Float, nullable=False) # Celsius? Kelvin? Just a value for now.
    gravity = Column(Float, default=1.0, nullable=False) # Relative to Earth (1.0)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    owner = relationship("User", backref="planets")
