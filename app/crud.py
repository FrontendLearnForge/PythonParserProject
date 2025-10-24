from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate
from typing import List, Optional




def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
):
    query = db.query(Product)

    if search:
        # Поиск по названию или бренду
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.brand.ilike(f"%{search}%")
            )
        )

    return query.offset(skip).limit(limit).all()


def create_product(db: Session, product: ProductCreate):
    db_product = Product(
        current_price=product.current_price,
        old_price=product.old_price,
        discount=product.discount,
        brand=product.brand,
        name=product.name,
        rating=product.rating,
        reviews_count=product.reviews_count,
        stock=product.stock,
        currency=product.currency
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def create_product_bulk(db: Session, products: List[ProductCreate]):
    """Добавление нескольких товаров"""
    db_products = []
    for product_data in products:
        db_product = Product(
            current_price=product_data.current_price,
            old_price=product_data.old_price,
            discount=product_data.discount,
            brand=product_data.brand,
            name=product_data.name,
            rating=product_data.rating,
            reviews_count=product_data.reviews_count,
            stock=product_data.stock,
            currency=product_data.currency
        )
        db.add(db_product)
        db_products.append(db_product)

    db.commit()
    for product in db_products:
        db.refresh(product)
    return db_products


def update_product(db: Session, product_id: int, product: ProductUpdate):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        update_data = product.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        db.commit()
        db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product