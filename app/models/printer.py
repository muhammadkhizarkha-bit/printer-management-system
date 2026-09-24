from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from ..database import Base


class Printer(Base):
    __tablename__ = "printers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)  # Printer, Cartridge, PCR, Charger Roller, Drum, Blade
    image = Column(String(255), default="")
    price = Column(Float, nullable=False, default=0)
    stock = Column(Integer, nullable=False, default=0)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
