from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..config import TEMPLATES_DIR
from ..database import get_db
from ..dependencies import require_user
from ..models.invoice import Invoice
from ..models.user import User
from ..utils.pdf_generator import invoice_pdf

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/invoices", response_class=HTMLResponse)
def list_invoices(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)):
    q = db.query(Invoice).join(Invoice.order)
    if user.role != "admin":
        q = q.filter(Invoice.order.has(customer_id=user.id))
    invoices = q.order_by(Invoice.id.desc()).all()
    return templates.TemplateResponse(request, "invoices.html", {
        "request": request, "user": user, "invoices": invoices,
    })


@router.get("/invoices/{iid}", response_class=HTMLResponse)
def view_invoice(iid: int, request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)):
    inv = db.query(Invoice).get(iid)
    if not inv:
        raise HTTPException(404, "Invoice not found")
    if user.role != "admin" and inv.order.customer_id != user.id:
        raise HTTPException(403, "Forbidden")
    return templates.TemplateResponse(request, "invoice.html", {
        "request": request, "user": user, "inv": inv, "order": inv.order,
        "customer": inv.order.customer, "printer": inv.order.printer,
    })


@router.get("/invoices/{iid}/pdf")
def invoice_download(iid: int, db: Session = Depends(get_db), user: User = Depends(require_user)):
    inv = db.query(Invoice).get(iid)
    if not inv:
        raise HTTPException(404, "Invoice not found")
    if user.role != "admin" and inv.order.customer_id != user.id:
        raise HTTPException(403, "Forbidden")
    pdf = invoice_pdf(inv, inv.order, inv.order.customer, inv.order.printer)
    return Response(content=pdf, media_type="application/pdf", headers={
        "Content-Disposition": f'attachment; filename="{inv.invoice_number}.pdf"'
    })
