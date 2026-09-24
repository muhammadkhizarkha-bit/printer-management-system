import re
from pydantic import BaseModel, EmailStr, field_validator, Field


CNIC_RE = re.compile(r"^\d{5}-\d{7}-\d$|^\d{13}$")
PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$")


class SignupIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    cnic: str
    email: EmailStr
    phone: str = Field(min_length=7, max_length=20)
    address: str = Field(min_length=2, max_length=255)
    password: str
    confirm_password: str

    @field_validator("cnic")
    @classmethod
    def _cnic(cls, v: str) -> str:
        if not CNIC_RE.match(v):
            raise ValueError("CNIC must be 13 digits or formatted as 12345-1234567-1")
        return v

    @field_validator("password")
    @classmethod
    def _pw(cls, v: str) -> str:
        if not PASSWORD_RE.match(v):
            raise ValueError(
                "Password must be 8+ chars with upper, lower, number and special character"
            )
        return v

    @field_validator("confirm_password")
    @classmethod
    def _match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str
    remember: bool = False


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
