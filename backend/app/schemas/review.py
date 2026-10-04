from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    product_id: int = Field(gt=0, le=9223372036854775807)
    rating: int = Field(ge=1, le=5, strict=True)
    title: str = Field(min_length=3, max_length=160)
    body: str = Field(min_length=10, max_length=5000)


class ReviewResponse(BaseModel):
    id: int
    rating: int
    title: str
    body: str
    author: str
    created_at: datetime


class ReviewSubmission(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    rating: int
    title: str
    body: str
    is_approved: bool
    created_at: datetime


class ReviewPage(BaseModel):
    items: list[ReviewResponse]
    average_rating: Decimal | None
    total: int
    page: int
    page_size: int
    total_pages: int
