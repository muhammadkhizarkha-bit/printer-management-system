from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..config import TEMPLATES_DIR
from ..database import get_db
from ..dependencies import require_admin, get_current_user
from ..models.printer import Printer
from ..models.user import User
from ..utils.helper import save_upload

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

CATEGORIES = ["Printer", "Cartridge", "PCR", "Charger Roller", "Drum", "Blade"]


@router.get("/printers", response_class=HTMLResponse)
def list_printers(request: Request, db: Session = Depends(get_db),
                  user: Optional[User] = Depends(get_current_user),
                  q: str = "", category: str = ""):
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    query = db.query(Printer)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Printer.name.ilike(like), Printer.description.ilike(like)))
    if category:
        query = query.filter(Printer.category == category)
    items = query.order_by(Printer.id.desc()).all()
    return templates.TemplateResponse(request, "printers.html", {
        "request": request, "user": user, "items": items, "q": q,
        "category": category, "categories": CATEGORIES,
    })


@router.post("/printers/add")
async def add_printer(db: Session = Depends(get_db), user: User = Depends(require_admin),
                      name: str = Form(...), category: str = Form(...),
                      price: float = Form(...), stock: int = Form(...),
                      description: str = Form(""), image: UploadFile = File(None)):
    img = save_upload(image) if image else ""
    db.add(Printer(name=name, category=category, price=price, stock=stock,
                   description=description, image=img))
    db.commit()
    return RedirectResponse(url="/printers", status_code=303)


@router.post("/printers/{pid}/edit")
async def edit_printer(pid: int, db: Session = Depends(get_db), user: User = Depends(require_admin),
                       name: str = Form(...), category: str = Form(...),
                       price: float = Form(...), stock: int = Form(...),
                       description: str = Form(""), image: UploadFile = File(None)):
    p = db.query(Printer).get(pid)
    if p:
        p.name, p.category, p.price, p.stock, p.description = name, category, price, stock, description
        if image and image.filename:
            new_img = save_upload(image)
            if new_img:
                p.image = new_img
        db.commit()
    return RedirectResponse(url="/printers", status_code=303)


@router.post("/printers/{pid}/delete")
def del_printer(pid: int, db: Session = Depends(get_db), user: User = Depends(require_admin)):
    p = db.query(Printer).get(pid)
    if p:
        db.delete(p)
        db.commit()
    return RedirectResponse(url="/printers", status_code=303)
