from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from .product import ProductSummary


class ProductSelection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_id: int = Field(gt=0)


class AddCartItem(ProductSelection):
    quantity: int = Field(default=1, ge=1, le=10000, strict=True)


class SetQuantity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    quantity: int = Field(ge=1, le=10000, strict=True)


class CartLine(BaseModel):
    id: int
    product: ProductSummary
    quantity: int
    subtotal: Decimal
    available: bool


class CartResponse(BaseModel):
    items: list[CartLine]
    item_count: int
    subtotal: Decimal
    shipping: Decimal
    total: Decimal
    free_shipping_threshold: Decimal
