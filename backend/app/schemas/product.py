from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from .brand import BrandResponse
from .category import CategoryResponse


class ProductFilters(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    lang: Literal["en", "tr"] = "en"
    search: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=50)
    brand: str | None = Field(default=None, max_length=50)
    min_price: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    max_price: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    sort: Literal["name_asc", "name_desc", "price_asc", "price_desc", "newest"] = (
        "name_asc"
    )
    page: int = Field(default=1, ge=1, le=2147483647)
    page_size: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def price_range(self):
        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise ValueError("min_price must be less than or equal to max_price")
        return self


class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    alt_text: str
    alt_text_tr: str = ""
    position: int


class ProductSpecificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str


class ProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    sku: str
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2, examples=["89.00"])
    stock_quantity: int
    category: CategoryResponse
    brand: BrandResponse
    images: list[ProductImageResponse]

    @computed_field
    @property
    def in_stock(self) -> bool:
        return self.stock_quantity > 0


class ProductDetail(ProductSummary):
    description: str
    specifications: list[ProductSpecificationResponse]
    created_at: datetime
    updated_at: datetime


class ProductPage(BaseModel):
    items: list[ProductSummary]
    total: int
    page: int
    page_size: int
    total_pages: int
