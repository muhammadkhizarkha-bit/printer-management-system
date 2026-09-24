from pydantic import BaseModel, EmailStr


class CustomerIn(BaseModel):
    name: str
    phone: str
    address: str
    email: EmailStr
    cnic: str


class CustomerOut(CustomerIn):
    id: int

    class Config:
        from_attributes = True
