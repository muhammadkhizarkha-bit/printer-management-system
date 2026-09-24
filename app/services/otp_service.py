import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.user import OTPCode

OTP_TTL_SECONDS = 120
MAX_ATTEMPTS = 3


def generate_otp(db: Session, phone: str) -> str:
    code = f"{random.randint(0, 999999):06d}"

    # Remove old OTPs
    db.query(OTPCode).filter(OTPCode.phone == phone).delete()

    otp = OTPCode(
        phone=phone,
        code=code,
        expires_at=datetime.utcnow() + timedelta(seconds=OTP_TTL_SECONDS),
        attempts=0,
        consumed=False,
    )

    db.add(otp)
    db.commit()

    print(f"[OTP] {phone} -> {code} (valid 2 minutes)")

    return code


def verify_otp(db: Session, phone: str, code: str):
    otp = (
        db.query(OTPCode)
        .filter(
            OTPCode.phone == phone,
            OTPCode.consumed == False,
        )
        .order_by(OTPCode.id.desc())
        .first()
    )

    if otp is None:
        return False, "OTP not found."

    # Expiry check
    if otp.expires_at < datetime.utcnow():
        return False, "OTP expired."

    # Maximum attempts
    if otp.attempts >= MAX_ATTEMPTS:
        return False, "Too many attempts."

    # Wrong code
    if otp.code != code:
        otp.attempts += 1
        db.commit()
        return False, "Invalid OTP."

    # Success
    otp.consumed = True
    db.commit()

    return True, "OTP verified successfully."