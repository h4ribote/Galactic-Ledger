from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint, BigInteger, DECIMAL
from sqlalchemy.orm import relationship
from app.models.base import Base

class Balance(Base):
    __tablename__ = "balances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    currency_type = Column(String(10), nullable=False) # CRED, IND, TECH, MIL, VOID
    amount = Column(DECIMAL(26, 0), default=0, nullable=False)

    # User relationship: user.balances will return a list of Balance objects
    user = relationship("User", backref="balances")

    __table_args__ = (
        UniqueConstraint('user_id', 'currency_type', name='uix_user_currency'),
    )
