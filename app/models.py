import uuid
from sqlalchemy import Column, Integer, String, Numeric, Boolean, Enum as SQLEnum, ForeignKey, Table, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from .database import Base
import enum


class SexEnum(str, enum.Enum):
    men = "men"
    women = "women"
    unisex = "unisex"


# ПРОМЕЖУТОЧНАЯ ТАБЛИЦА ДЛЯ ЦВЕТОВ ТОВАРА
product_colors = Table(
    'product_colors',
    Base.metadata,
    Column('product_id', UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
    Column('color_id', Integer, ForeignKey('colors.id', ondelete='CASCADE'), primary_key=True)
)

# НОВАЯ ПРОМЕЖУТОЧНАЯ ТАБЛИЦА ДЛЯ ВИШЛИСТА (Многие-ко-многим: Юзер <-> Товар)
user_wishlist = Table(
    'user_wishlist',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('product_id', UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), primary_key=True)
)


class Color(Base):
    __tablename__ = "colors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    hex_code = Column(String, nullable=False)


class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    address = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    inventory = relationship("StoreInventory", back_populates="store", cascade="all, delete-orphan")


class StoreInventory(Base):
    __tablename__ = "store_inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    store_id = Column(Integer, ForeignKey('stores.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    product = relationship("Product", back_populates="inventory")
    store = relationship("Store", back_populates="inventory")


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    street_name = Column(String, nullable=False)
    house_number = Column(String, nullable=False)
    post_code = Column(String, nullable=False)
    city = Column(String, nullable=False)

    # ИСПРАВЛЕНО: Тип изменен на UUID, чтобы совпадать с User.id
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="addresses")


class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    sex = Column(SQLEnum(SexEnum), nullable=False)
    sub_category = Column(String, index=True, nullable=True)
    category = Column(String, index=True, nullable=False)
    sizes = Column(ARRAY(String), nullable=False)
    brand = Column(String, nullable=False, default="Unknown")
    material = Column(String, nullable=True)
    country_of_origin = Column(String, nullable=True)
    image_url = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    colors = relationship("Color", secondary=product_colors, lazy="joined")
    inventory = relationship("StoreInventory", back_populates="product", cascade="all, delete-orphan")


# НОВАЯ МОДЕЛЬ: ЗАКАЗЫ (Один-ко-многим с User)
class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = Column(String, default="pending", nullable=False)  # например: pending, paid, shipped, delivered
    total_amount = Column(Numeric(10, 2), nullable=False)

    user = relationship("User", back_populates="orders")
    # Здесь в будущем можно добавить связь с товарами в заказе (OrderItems)


class User(Base):
    __tablename__ = "users"
    # ИСПРАВЛЕНО: Добавлен default=uuid.uuid4
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    # E-commerce данные
    phone_number = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)

    # Физические параметры для ИИ
    height_cm = Column(Integer, nullable=True)
    top_size = Column(String, nullable=True)
    bottom_size = Column(String, nullable=True)
    shoe_size = Column(Numeric(3, 1), nullable=True)

    # Предпочтения для ИИ
    preferred_fit = Column(String, nullable=True)
    favorite_colors = Column(ARRAY(String), nullable=True)
    style_aesthetics = Column(ARRAY(String), nullable=True)

    # Связи
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    wishlist_items = relationship("Product", secondary=user_wishlist, lazy="joined")