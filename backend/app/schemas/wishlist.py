from pydantic import BaseModel

from .product import ProductSummary


class WishlistLine(BaseModel):
    product: ProductSummary
    available: bool


class WishlistResponse(BaseModel):
    items: list[WishlistLine]
