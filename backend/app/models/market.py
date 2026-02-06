from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class MarketOrder(Base):
    __tablename__ = "market_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    planet_id = Column(Integer, ForeignKey("planets.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    order_type = Column(String(10), nullable=False) # 'BUY' or 'SELL'
    currency_type = Column(String(10), default='CRED', nullable=False)
    price = Column(DECIMAL(26, 0), nullable=False)
    quantity = Column(Integer, nullable=False)
    filled_quantity = Column(Integer, default=0)
    status = Column(String(20), default="OPEN") # 'OPEN', 'FILLED', 'CANCELLED'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    planet = relationship("Planet")
    item = relationship("Item")
