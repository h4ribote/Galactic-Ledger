from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Optional because fleet might imply owner, but better explicit
    planet_id = Column(Integer, ForeignKey("planets.id"), nullable=True)
    fleet_id = Column(Integer, ForeignKey("fleets.id"), nullable=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)

    user = relationship("User", backref="inventories")
    planet = relationship("Planet", backref="inventories")
    fleet = relationship("Fleet", backref="inventories")
    item = relationship("Item")
