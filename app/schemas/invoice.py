from pydantic import BaseModel


class InvoiceOut(BaseModel):
    id: int
    invoice_number: str
    order_id: int
    subtotal: float
    gst: float
    total: float

    class Config:
        from_attributes = True
