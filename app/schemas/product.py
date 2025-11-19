from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = ""
    price: Optional[int] = 0
    active: Optional[bool] = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        orm_mode = True   # <--- THIS MUST BE PRESENT
