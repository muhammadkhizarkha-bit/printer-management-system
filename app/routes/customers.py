from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..config import TEMPLATES_DIR
from ..database import get_db
from ..dependencies import require_admin
from ..models.customer import Customer
from ..models.user import User

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

PAGE_SIZE = 8


@router.get("/customers", response_class=HTMLResponse)
def list_customers(request: Request, db: Session = Depends(get_db),
                   user: User = Depends(require_admin), q: str = "", page: int = 1):
    query = db.query(Customer)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Customer.name.ilike(like), Customer.email.ilike(like), Customer.phone.ilike(like)))
    total = query.count()
    items = query.order_by(Customer.id.desc()).offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE).all()
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    return templates.TemplateResponse(request, "customers.html", {
        "request": request, "user": user, "customers": items, "q": q,
        "page": page, "pages": pages, "total": total,
    })


@router.post("/customers/add")
def add_customer(db: Session = Depends(get_db), user: User = Depends(require_admin),
                 name: str = Form(...), phone: str = Form(...), address: str = Form(...),
                 email: str = Form(...), cnic: str = Form(...)):
    db.add(Customer(name=name, phone=phone, address=address, email=email, cnic=cnic))
    db.commit()
    return RedirectResponse(url="/customers", status_code=303)


@router.post("/customers/{cid}/edit")
def edit_customer(cid: int, db: Session = Depends(get_db), user: User = Depends(require_admin),
                  name: str = Form(...), phone: str = Form(...), address: str = Form(...),
                  email: str = Form(...), cnic: str = Form(...)):
    c = db.query(Customer).get(cid)
    if c:
        c.name, c.phone, c.address, c.email, c.cnic = name, phone, address, email, cnic
        db.commit()
    return RedirectResponse(url="/customers", status_code=303)


@router.post("/customers/{cid}/delete")
def del_customer(cid: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    c = db.query(Customer).get(cid)
    if c:
        db.delete(c)
        db.commit()
    return RedirectResponse(url="/customers", status_code=303)
