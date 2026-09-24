from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from ..database import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    email = Column(String(120), nullable=False)
    cnic = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
