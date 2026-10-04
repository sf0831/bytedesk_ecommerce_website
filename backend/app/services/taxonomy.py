from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Brand, Category
from ..schemas.category import CategoryResponse
from .errors import NotFoundError


def list_categories(db: Session) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name, Category.id)))


def get_category(db: Session, slug: str) -> Category:
    category = db.scalar(select(Category).where(Category.slug == slug))
    if category is None:
        raise NotFoundError("Category not found", code="category_not_found")
    return category


def list_brands(db: Session) -> list[Brand]:
    return list(db.scalars(select(Brand).order_by(Brand.name, Brand.id)))


def get_brand(db: Session, slug: str) -> Brand:
    brand = db.scalar(select(Brand).where(Brand.slug == slug))
    if brand is None:
        raise NotFoundError("Brand not found", code="brand_not_found")
    return brand


def localized_category(category: Category, lang: str) -> CategoryResponse:
    result = CategoryResponse.model_validate(category)
    if lang == "tr":
        result.name = category.name_tr or category.name
    return result
