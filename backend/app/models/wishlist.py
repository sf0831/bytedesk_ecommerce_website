from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .product import Product


class Wishlist(Base):
    __tablename__ = "wishlists"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    wishlist_id: Mapped[int] = mapped_column(ForeignKey("wishlists.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped[Product] = relationship()
