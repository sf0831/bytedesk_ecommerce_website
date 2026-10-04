from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import UUID4, BaseModel, ConfigDict, Field


class CheckoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    checkout_key: UUID4
    shipping_name: str = Field(min_length=2, max_length=200)
    shipping_address: str = Field(min_length=5, max_length=300)
    shipping_city: str = Field(min_length=2, max_length=100)
    shipping_postal_code: str = Field(min_length=2, max_length=20)
    shipping_country: str = Field(min_length=2, max_length=100)


class OrderLine(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int | None
    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal


class OrderSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: Literal[
        "pending", "confirmed", "processing", "shipped", "delivered", "cancelled"
    ]
    subtotal: Decimal
    shipping: Decimal
    total: Decimal
    created_at: datetime
    items: list[OrderLine]


class OrderDetail(OrderSummary):
    shipping_name: str
    shipping_address: str
    shipping_city: str
    shipping_postal_code: str
    shipping_country: str


class OrderPage(BaseModel):
    items: list[OrderSummary]
    total: int
    page: int
    page_size: int
    total_pages: int
