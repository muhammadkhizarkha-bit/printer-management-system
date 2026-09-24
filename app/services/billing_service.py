from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models.order import Order
from ..models.invoice import Invoice
from ..config import GST_RATE


def compute_totals(unit_price: float, quantity: int):
    subtotal = round(unit_price * quantity, 2)
    gst = round(subtotal * GST_RATE, 2)
    total = round(subtotal + gst, 2)
    return subtotal, gst, total


def create_invoice_for_order(db: Session, order: Order) -> Invoice:
    if order.invoice:
        return order.invoice
    number = f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{order.id:05d}"
    inv = Invoice(
        invoice_number=number,
        order_id=order.id,
        subtotal=order.subtotal,
        gst=order.gst,
        total=order.total,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv
