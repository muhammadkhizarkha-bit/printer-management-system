import csv
import io
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.order import Order
from ..models.invoice import Invoice
from ..models.user import User
from ..models.printer import Printer


def summary(db: Session) -> dict:
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    pending = db.query(func.count(Order.id)).filter(Order.status == "Pending").scalar() or 0
    approved = db.query(func.count(Order.id)).filter(Order.status == "Approved").scalar() or 0
    completed = db.query(func.count(Order.id)).filter(Order.status == "Completed").scalar() or 0
    revenue = db.query(func.coalesce(func.sum(Invoice.total), 0)).scalar() or 0
    gst = db.query(func.coalesce(func.sum(Invoice.gst), 0)).scalar() or 0
    customers = db.query(func.count(User.id)).filter(User.role == "customer").scalar() or 0
    stock_items = db.query(func.count(Printer.id)).scalar() or 0
    return {
        "total_orders": total_orders,
        "pending": pending,
        "approved": approved,
        "completed": completed,
        "revenue": round(float(revenue), 2),
        "gst": round(float(gst), 2),
        "customers": customers,
        "stock_items": stock_items,
    }


def orders_csv(db: Session) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Order ID", "Customer", "Printer", "Qty", "Total", "Status", "Date"])
    for o in db.query(Order).all():
        w.writerow([
            o.id,
            o.customer.full_name if o.customer else "",
            o.printer.name if o.printer else "",
            o.quantity,
            o.total,
            o.status,
            o.created_at.strftime("%Y-%m-%d"),
        ])
    return buf.getvalue()
