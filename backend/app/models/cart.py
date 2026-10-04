from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .product import Product


class Cart(Base):
    __tablename__ = "carts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CartItem(Base):
    __tablename__ = "cart_items"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    product: Mapped[Product] = relationship()
