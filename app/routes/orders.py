from fastapi import APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..config import TEMPLATES_DIR
from ..database import get_db
from ..dependencies import require_user, require_admin
from ..models.order import Order
from ..models.printer import Printer
from ..models.user import User
from ..services.billing_service import compute_totals, create_invoice_for_order

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/orders/new", response_class=HTMLResponse)
def new_order_page(request: Request, db: Session = Depends(get_db),
                   user: User = Depends(require_user), printer_id: int = 0):
    printers = db.query(Printer).filter(Printer.stock > 0).all()
    selected = db.query(Printer).get(printer_id) if printer_id else None
    return templates.TemplateResponse(request, "new_order.html", {
        "request": request, "user": user, "printers": printers, "selected": selected,
    })


@router.post("/orders/new")
def create_order(db: Session = Depends(get_db), user: User = Depends(require_user),
                 printer_id: int = Form(...), quantity: int = Form(1),
                 address: str = Form(...), payment_method: str = Form("COD")):
    printer = db.query(Printer).get(printer_id)
    if not printer:
        raise HTTPException(404, "Printer not found")
    if quantity < 1 or quantity > printer.stock:
        return RedirectResponse(url="/orders/new?error=Invalid+quantity", status_code=303)
    subtotal, gst, total = compute_totals(printer.price, quantity)
    order = Order(
        customer_id=user.id, printer_id=printer.id, quantity=quantity, address=address,
        payment_method=payment_method, unit_price=printer.price,
        subtotal=subtotal, gst=gst, total=total, status="Pending",
    )
    db.add(order)
    printer.stock -= quantity
    db.commit()
    db.refresh(order)
    return RedirectResponse(url="/orders", status_code=303)


@router.get("/orders", response_class=HTMLResponse)
def list_orders(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)):
    if user.role == "admin":
        orders = db.query(Order).order_by(Order.id.desc()).all()
    else:
        orders = db.query(Order).filter(Order.customer_id == user.id).order_by(Order.id.desc()).all()
    return templates.TemplateResponse(request, "orders.html", {
        "request": request, "user": user, "orders": orders,
    })


@router.post("/orders/{oid}/status")
def set_status(oid: int, db: Session = Depends(get_db),
               user: User = Depends(require_admin), status: str = Form(...)):
    if status not in {"Pending", "Approved", "Cancelled", "Completed"}:
        raise HTTPException(400, "Bad status")
    order = db.query(Order).get(oid)
    if not order:
        raise HTTPException(404, "Order not found")
    prev = order.status
    order.status = status
    if status in ("Approved", "Completed") and not order.invoice:
        create_invoice_for_order(db, order)
    if status == "Cancelled" and prev != "Cancelled":
        order.printer.stock += order.quantity
    db.commit()
    return RedirectResponse(url="/orders", status_code=303)
