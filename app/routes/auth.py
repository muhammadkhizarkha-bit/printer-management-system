from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import ValidationError

from ..config import TEMPLATES_DIR
from ..database import get_db
from ..models.user import User
from ..schemas.auth import SignupIn
from ..services.auth_service import hash_password, verify_password, create_access_token
from ..services.otp_service import generate_otp

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: str = "", info: str = ""):
    return templates.TemplateResponse(request, "login.html", {"request": request, "error": error, "info": info, "user": None})


@router.post("/login")
def login(
    response: Response,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
    remember: str = Form(default=""),
):
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse(url="/login?error=Invalid+credentials", status_code=303)
    if not user.is_active or not user.phone_verified:
        return RedirectResponse(url=f"/verify-otp?phone={user.phone}&info=Please+verify+your+phone", status_code=303)
    token = create_access_token({"sub": str(user.id), "role": user.role}, remember=bool(remember))
    resp = RedirectResponse(url="/dashboard", status_code=303)
    max_age = 60 * 60 * 24 * 7 if remember else 60 * 60
    resp.set_cookie("access_token", token, httponly=True, samesite="lax", max_age=max_age)
    return resp


@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/login?info=Logged+out", status_code=303)
    resp.delete_cookie("access_token")
    return resp


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request, error: str = ""):
    return templates.TemplateResponse(request, "signup.html", {"request": request, "error": error, "user": None})


@router.post("/signup")
def signup(
    db: Session = Depends(get_db),
    full_name: str = Form(...),
    cnic: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    try:
        data = SignupIn(
            full_name=full_name, cnic=cnic, email=email, phone=phone,
            address=address, password=password, confirm_password=confirm_password,
        )
    except ValidationError as e:
        msg = "; ".join(err["msg"] for err in e.errors())
        return RedirectResponse(url=f"/signup?error={msg}", status_code=303)

    if db.query(User).filter((User.email == data.email.lower()) | (User.phone == data.phone) | (User.cnic == data.cnic)).first():
        return RedirectResponse(url="/signup?error=User+with+email,+phone+or+CNIC+already+exists", status_code=303)

    user = User(
        full_name=data.full_name,
        cnic=data.cnic,
        email=data.email.lower(),
        phone=data.phone,
        address=data.address,
        hashed_password=hash_password(data.password),
        role="customer",
        is_active=False,
        phone_verified=False,
    )
    db.add(user)
    db.commit()
    code = generate_otp(db, data.phone)
    return RedirectResponse(
        url=f"/verify-otp?phone={data.phone}&info=Your+OTP+(demo):+{code}",
        status_code=303,
    )
