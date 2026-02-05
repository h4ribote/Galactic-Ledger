from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    issuer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contractor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    origin_planet_id = Column(Integer, ForeignKey("planets.id"), nullable=False)
    destination_planet_id = Column(Integer, ForeignKey("planets.id"), nullable=False)

    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    currency_type = Column(String(10), default="CRED", nullable=False)
    reward_amount = Column(Float, nullable=False)
    collateral_amount = Column(Float, nullable=False)
    duration_seconds = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)

    status = Column(String(20), default="OPEN", nullable=False) # OPEN, IN_PROGRESS, COMPLETED, FAILED

    issuer = relationship("User", foreign_keys=[issuer_id], backref="issued_contracts")
    contractor = relationship("User", foreign_keys=[contractor_id], backref="accepted_contracts")
    origin_planet = relationship("Planet", foreign_keys=[origin_planet_id])
    destination_planet = relationship("Planet", foreign_keys=[destination_planet_id])
    item = relationship("Item")
