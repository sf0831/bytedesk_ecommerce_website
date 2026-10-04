from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    checkout_key: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)
    status: Mapped[str] = mapped_column(String(20))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    shipping: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    shipping_name: Mapped[str] = mapped_column(String(200))
    shipping_address: Mapped[str] = mapped_column(String(300))
    shipping_city: Mapped[str] = mapped_column(String(100))
    shipping_postal_code: Mapped[str] = mapped_column(String(20))
    shipping_country: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    items: Mapped[list["OrderItem"]] = relationship(order_by="OrderItem.id")


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id"), nullable=True
    )
    product_name: Mapped[str] = mapped_column(String(200))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    quantity: Mapped[int] = mapped_column(Integer)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))
