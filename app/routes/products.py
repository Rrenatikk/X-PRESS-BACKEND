import uuid
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models import Product
# Импортируем схемы, модели и зависимость для БД
from ..schemas import ProductSchema, ProductSchemaCreate, ProductSchemaUpdate
from .. import models
from ..database import get_db

router = APIRouter(prefix="/products", tags=["products"])


# GET: Возвращает список всех продуктов из БД
@router.get("/", response_model=List[ProductSchema])
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products

# ВАЖНО: Эндпоинт /search должен идти ДО /{product_id}
# Иначе FastAPI воспримет слово "search" как UUID и выдаст ошибку валидации!
# Путь будет /products/search благодаря prefix="/products"
@router.get("/search", response_model=List[ProductSchema])
async def search_products(
        q: str = Query(..., description="Search query string"),
        db: Session = Depends(get_db)
):
    search_format = f"%{q}%"

    products = db.query(Product).filter(
        or_(
            Product.title.ilike(search_format),
            Product.category.ilike(search_format),
            Product.brand.ilike(search_format),  # Поиск по бренду
            Product.material.ilike(search_format),  # Поиск по материалу (например, "cotton")
            Product.description.ilike(search_format)  # Поиск по тексту описания
        )
    ).all()

    return products


# GET: Поиск по UUID в БД
@router.get("/{product_id}", response_model=ProductSchema)
def get_product(product_id: uuid.UUID, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# POST: Создание продукта в БД
@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
def create_product(new_product: ProductSchemaCreate, db: Session = Depends(get_db)):
    # Превращаем Pydantic схему в словарь и распаковываем в модель SQLAlchemy
    db_product = models.Product(**new_product.model_dump())

    db.add(db_product)
    db.commit()  # Сохраняем изменения в БД
    db.refresh(db_product)  # Обновляем объект, чтобы получить сгенерированный базой id

    return db_product


# PUT: Полное обновление продукта
@router.put("/{product_id}", response_model=ProductSchema)
def update_product(product_id: uuid.UUID, updated_product: ProductSchemaCreate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Обновляем все поля
    update_data = updated_product.model_dump()
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


# PATCH: Частичное обновление продукта
@router.patch("/{product_id}", response_model=ProductSchema)
def patch_product(product_id: uuid.UUID, updated_fields: ProductSchemaUpdate, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # exclude_unset=True гарантирует, что мы применим только те поля, которые передал клиент
    update_data = updated_fields.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


# DELETE: Удаление из БД
@router.delete("/{product_id}")
def delete_product(product_id: uuid.UUID, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    return {"detail": f"Product {product_id} deleted successfully"}