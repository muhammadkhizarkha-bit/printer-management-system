from pydantic import BaseModel


class PrinterIn(BaseModel):
    name: str
    category: str
    price: float
    stock: int
    description: str = ""
    image: str = ""


class PrinterOut(PrinterIn):
    id: int

    class Config:
        from_attributes = True
