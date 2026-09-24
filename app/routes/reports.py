from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..config import TEMPLATES_DIR
from ..database import get_db
from ..dependencies import require_admin
from ..models.user import User
from ..services.report_service import summary, orders_csv
from ..utils.pdf_generator import report_pdf

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/reports", response_class=HTMLResponse)
def reports(request: Request, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    s = summary(db)
    return templates.TemplateResponse(request, "reports.html", {"request": request, "user": user, "s": s})


@router.get("/reports/csv")
def reports_csv(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    csv_text = orders_csv(db)
    return Response(content=csv_text, media_type="text/csv", headers={
        "Content-Disposition": 'attachment; filename="orders.csv"'
    })


@router.get("/reports/pdf")
def reports_pdf(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    s = summary(db)
    rows = [
        ("Total Customers", s["customers"]),
        ("Total Orders", s["total_orders"]),
        ("Pending Orders", s["pending"]),
        ("Approved Orders", s["approved"]),
        ("Completed Orders", s["completed"]),
        ("Revenue", f"{s['revenue']:.2f}"),
        ("GST Collected", f"{s['gst']:.2f}"),
        ("Inventory Items", s["stock_items"]),
    ]
    pdf = report_pdf("Business Report", rows)
    return Response(content=pdf, media_type="application/pdf", headers={
        "Content-Disposition": 'attachment; filename="report.pdf"'
    })
