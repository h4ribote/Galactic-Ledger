from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String, UniqueConstraint, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False)

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="wallet", uselist=False)
    balances = relationship("WalletBalance", backref="wallet", cascade="all, delete-orphan")

class WalletBalance(Base):
    __tablename__ = "wallet_balances"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    currency_type = Column(String(10), nullable=False) # CRED, IND, TECH, MIL, VOID
    amount = Column(Float, default=0.0, nullable=False)

    __table_args__ = (
        UniqueConstraint('wallet_id', 'currency_type', name='uix_wallet_currency'),
    )
