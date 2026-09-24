from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..config import TEMPLATES_DIR
from ..database import get_db
from ..models.user import User
from ..services.otp_service import generate_otp, verify_otp

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/verify-otp", response_class=HTMLResponse)
def verify_page(request: Request, phone: str = "", info: str = "", error: str = ""):
    return templates.TemplateResponse(request, "verify_otp.html",
        {"request": request, "phone": phone, "info": info, "error": error, "user": None},
    )


@router.post("/verify-otp")
def do_verify(db: Session = Depends(get_db), phone: str = Form(...), code: str = Form(...)):
    ok, msg = verify_otp(db, phone, code)
    if not ok:
        return RedirectResponse(url=f"/verify-otp?phone={phone}&error={msg}", status_code=303)
    user = db.query(User).filter(User.phone == phone).first()
    if user:
        user.phone_verified = True
        user.is_active = True
        db.commit()
    return RedirectResponse(url="/login?info=Account+verified.+Please+log+in.", status_code=303)


@router.post("/resend-otp")
def resend(db: Session = Depends(get_db), phone: str = Form(...)):
    code = generate_otp(db, phone)
    return RedirectResponse(
        url=f"/verify-otp?phone={phone}&info=New+OTP+(demo):+{code}",
        status_code=303,
    )
