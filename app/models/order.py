from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    printer_id = Column(Integer, ForeignKey("printers.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    address = Column(String(255), nullable=False)
    payment_method = Column(String(50), nullable=False, default="COD")
    unit_price = Column(Float, nullable=False, default=0)
    subtotal = Column(Float, nullable=False, default=0)
    gst = Column(Float, nullable=False, default=0)
    total = Column(Float, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="Pending")  # Pending/Approved/Cancelled/Completed
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("User", back_populates="orders")
    printer = relationship("Printer")
    invoice = relationship("Invoice", back_populates="order", uselist=False, cascade="all, delete-orphan")
