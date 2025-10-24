from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ProductBase(BaseModel):
    current_price: Optional[float] = None
    old_price: Optional[float] = None
    discount: Optional[int] = None
    brand: Optional[str] = None
    name: str
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    stock: Optional[str] = None
    currency: Optional[str] = "RUB"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    name: Optional[str] = None
    current_price: Optional[float] = None


class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None