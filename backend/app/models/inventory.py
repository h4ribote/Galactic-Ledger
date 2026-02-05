from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    planet_id = Column(Integer, ForeignKey("planets.id"), nullable=True)
    fleet_id = Column(Integer, ForeignKey("fleets.id"), nullable=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)

    planet = relationship("Planet", backref="inventory")
    fleet = relationship("Fleet", backref="inventory")
    item = relationship("Item")
