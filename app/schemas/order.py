from pydantic import BaseModel


class OrderIn(BaseModel):
    printer_id: int
    quantity: int = 1
    address: str
    payment_method: str = "COD"


class OrderStatusIn(BaseModel):
    status: str
