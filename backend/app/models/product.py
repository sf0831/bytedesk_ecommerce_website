from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .brand import Brand
from .category import Category


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(220), unique=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[str] = mapped_column(Text)
    description_tr: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    stock_quantity: Mapped[int] = mapped_column(Integer)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"))
    is_active: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    category: Mapped[Category] = relationship()
    brand: Mapped[Brand] = relationship()
    images: Mapped[list["ProductImage"]] = relationship(
        order_by="(ProductImage.position, ProductImage.id)"
    )
    specifications: Mapped[list["ProductSpecification"]] = relationship(
        order_by="ProductSpecification.id"
    )


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    url: Mapped[str] = mapped_column(String(500))
    alt_text: Mapped[str] = mapped_column(String(200))
    alt_text_tr: Mapped[str] = mapped_column(String(200), default="")
    position: Mapped[int] = mapped_column(Integer)


class ProductSpecification(Base):
    __tablename__ = "product_specifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    key: Mapped[str] = mapped_column(String(100))
    value: Mapped[str] = mapped_column(String(250))
    key_tr: Mapped[str] = mapped_column(String(100), default="")
    value_tr: Mapped[str] = mapped_column(String(250), default="")
