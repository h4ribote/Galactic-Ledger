from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    planet_id = Column(Integer, ForeignKey("planets.id"), nullable=False)
    type = Column(String(50), nullable=False)  # e.g., "IRON_MINE"
    status = Column(String(20), default="constructing", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    planet = relationship("Planet", backref="buildings")
