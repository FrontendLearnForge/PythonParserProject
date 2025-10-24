from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    current_price = Column(Float)
    old_price = Column(Float)
    discount = Column(Integer)
    brand = Column(String(100), index=True)
    name = Column(String(500), nullable=False, index=True)
    rating = Column(Float)
    reviews_count = Column(Integer)
    stock = Column(String(100))
    currency = Column(String(10), default="RUB")  # RUB, USD, EUR, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())