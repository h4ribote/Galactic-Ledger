from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Fleet(Base):
    __tablename__ = "fleets"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)

    location_planet_id = Column(Integer, ForeignKey("planets.id"), nullable=True)
    destination_planet_id = Column(Integer, ForeignKey("planets.id"), nullable=True)

    arrival_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="IDLE", nullable=False) # IDLE, TRANSIT
    cargo_capacity = Column(Float, default=100.0, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", backref="fleets")
    location = relationship("Planet", foreign_keys=[location_planet_id])
    destination = relationship("Planet", foreign_keys=[destination_planet_id])
