from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .config import STATIC_DIR, TEMPLATES_DIR
from .database import Base, engine, SessionLocal, get_db
from .models import User, Customer, Printer, Order, Invoice  # noqa: F401
from .services.auth_service import hash_password
from .services.printer_service import seed_printers
from .services.report_service import summary
from .dependencies import get_current_user, require_user
from .routes import auth, otp, customers, printers, orders, invoices, reports


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@printer.com").first():
            db.add(User(
                full_name="System Admin", cnic="00000-0000000-0",
                email="admin@printer.com", phone="03000000000",
                address="HQ", hashed_password=hash_password("Admin@123"),
                role="admin", is_active=True, phone_verified=True,
            ))
            db.commit()
        seed_printers(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Printer Management System", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/")
def root(user: Optional[User] = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), user: User = Depends(require_user)):
    if user.role == "admin":
        s = summary(db)
        recent_orders = db.query(Order).order_by(Order.id.desc()).limit(6).all()
        inv_items = db.query(Printer).order_by(Printer.stock.asc()).limit(6).all()
        return templates.TemplateResponse(request, "dashboard.html", {
            "request": request, "user": user, "s": s,
            "recent_orders": recent_orders, "inv_items": inv_items,
        })
    my_orders = db.query(Order).filter(Order.customer_id == user.id).order_by(Order.id.desc()).all()
    my_invoices = [o.invoice for o in my_orders if o.invoice]
    return templates.TemplateResponse(request, "dashboard.html", {
        "request": request, "user": user, "my_orders": my_orders, "my_invoices": my_invoices,
    })


app.include_router(auth.router)
app.include_router(otp.router)
app.include_router(customers.router)
app.include_router(printers.router)
app.include_router(orders.router)
app.include_router(invoices.router)
app.include_router(reports.router)
