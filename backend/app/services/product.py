from math import ceil

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from ..models import Brand, Category, Product
from ..schemas.product import ProductDetail, ProductFilters, ProductPage, ProductSummary
from .errors import NotFoundError


def list_products(db: Session, filters: ProductFilters) -> ProductPage:
    query = (
        select(Product)
        .join(Product.category)
        .join(Product.brand)
        .where(Product.is_active.is_(True))
    )
    if filters.search:
        query = query.where(
            or_(
                *[
                    field.icontains(filters.search, autoescape=True)
                    for field in (
                        Product.name,
                        Product.sku,
                        Product.description,
                        Product.description_tr,
                        Brand.name,
                        Category.name,
                        Category.name_tr,
                    )
                ]
            )
        )
    if filters.category:
        query = query.where(Category.slug == filters.category)
    if filters.brand:
        query = query.where(Brand.slug == filters.brand)
    if filters.min_price is not None:
        query = query.where(Product.price >= filters.min_price)
    if filters.max_price is not None:
        query = query.where(Product.price <= filters.max_price)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    sort_columns = {
        "name_asc": (Product.name.asc(),),
        "name_desc": (Product.name.desc(),),
        "price_asc": (Product.price.asc(), Product.name.asc()),
        "price_desc": (Product.price.desc(), Product.name.asc()),
        "newest": (Product.created_at.desc(),),
    }
    query = (
        query.options(
            joinedload(Product.category),
            joinedload(Product.brand),
            selectinload(Product.images),
        )
        .order_by(*sort_columns[filters.sort], Product.id.asc())
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
    )
    products = db.scalars(query).all()
    return ProductPage(
        items=[localize(product, filters.lang) for product in products],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=ceil(total / filters.page_size),
    )


def get_product(db: Session, slug: str, lang: str = "en") -> ProductDetail:
    product = db.scalar(
        select(Product)
        .where(Product.slug == slug, Product.is_active.is_(True))
        .options(
            joinedload(Product.category),
            joinedload(Product.brand),
            selectinload(Product.images),
            selectinload(Product.specifications),
        )
    )
    if product is None:
        raise NotFoundError("Product not found", code="product_not_found")
    return localize(product, lang, detail=True)


def localize(product: Product, lang: str, detail: bool = False):
    schema = ProductDetail if detail else ProductSummary
    result = schema.model_validate(product)
    if lang == "tr":
        result.category.name = product.category.name_tr or product.category.name
        if detail:
            result.description = product.description_tr or product.description
            for response, specification in zip(
                result.specifications, product.specifications, strict=True
            ):
                response.key = specification.key_tr or specification.key
                response.value = specification.value_tr or specification.value
    return result
