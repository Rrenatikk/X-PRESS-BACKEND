from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from decimal import Decimal
from enum import Enum
from datetime import date
import uuid


class SexEnum(str, Enum):
    men = "men"
    women = "women"
    unisex = "unisex"


class ColorSchema(BaseModel):
    id: int
    name: str
    hex_code: str
    model_config = ConfigDict(from_attributes=True)


class StoreSchema(BaseModel):
    id: int
    name: str
    city: str
    address: str
    postal_code: str
    latitude: float
    longitude: float
    model_config = ConfigDict(from_attributes=True)


class StoreInventorySchema(BaseModel):
    store: StoreSchema
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class AddressSchema(BaseModel):
    id: int
    street_name: str = Field(..., min_length=1, max_length=255)
    house_number: str = Field(..., min_length=1, max_length=255)
    post_code: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=255)
    model_config = ConfigDict(from_attributes=True)


# НОВАЯ СХЕМА: ЗАКАЗ
class OrderSchema(BaseModel):
    id: uuid.UUID
    status: str
    total_amount: Decimal
    model_config = ConfigDict(from_attributes=True)


class ProductSchemaCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    sex: SexEnum
    sub_category: str
    category: str
    sizes: List[str]
    colors_ids: Optional[List[int]] = None
    brand: str = Field(..., min_length=1)
    material: Optional[str] = None
    country_of_origin: Optional[str] = None
    image_url: str
    is_active: bool = True


class ProductSchema(ProductSchemaCreate):
    id: uuid.UUID
    colors: List[ColorSchema]
    inventory: List[StoreInventorySchema] = []
    model_config = ConfigDict(from_attributes=True)


class ProductSchemaUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, gt=0)
    sex: Optional[SexEnum] = None
    sub_category: Optional[str] = None
    category: Optional[str] = None
    sizes: Optional[List[str]] = None
    colors_ids: Optional[List[int]] = None
    brand: Optional[str] = Field(default=None, min_length=1)
    material: Optional[str] = None
    country_of_origin: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


# Базовая схема с общими полями
class UserBase(BaseModel):
    email: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)

    # E-commerce данные
    phone_number: Optional[str] = None
    birth_date: Optional[date] = None

    # Физические параметры
    height_cm: Optional[int] = None
    top_size: Optional[str] = None
    bottom_size: Optional[str] = None
    shoe_size: Optional[Decimal] = None

    # Предпочтения
    preferred_fit: Optional[str] = None
    favorite_colors: Optional[List[str]] = None
    style_aesthetics: Optional[List[str]] = None


# Схема для создания (Регистрация). Здесь мы ДОБАВЛЯЕМ пароль.
class UserProfileSchemaCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)


# Схема ответа (Отправка на фронтенд).
# Наследует всё из UserBase, но НЕ содержит пароль!
class UserProfileSchema(UserBase):
    id: uuid.UUID

    # Вложенные связи
    addresses: List[AddressSchema] = []
    orders: List[OrderSchema] = []
    wishlist_items: List[ProductSchema] = []

    model_config = ConfigDict(from_attributes=True)


# Схема для обновления (Например, в личном кабинете)
class UserProfileSchemaUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    phone_number: Optional[str] = None
    birth_date: Optional[date] = None
    height_cm: Optional[int] = None
    top_size: Optional[str] = None
    bottom_size: Optional[str] = None
    shoe_size: Optional[Decimal] = None
    preferred_fit: Optional[str] = None
    favorite_colors: Optional[List[str]] = None
    style_aesthetics: Optional[List[str]] = None

class UserLoginSchema(BaseModel):
    email: str
    password: str

# Добавь эту схему в schemas.py
class EmailCheckSchema(BaseModel):
    email: str