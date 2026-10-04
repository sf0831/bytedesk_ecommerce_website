from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..models import Product, Review
from ..schemas.review import ReviewCreate, ReviewPage, ReviewResponse
from .errors import StoreError


def active_product(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if product is None or not product.is_active:
        raise StoreError(404, "Product not found.", code="product_not_found")
    return product


def listing(db: Session, product_id: int, page: int, page_size: int) -> ReviewPage:
    active_product(db, product_id)
    conditions = (Review.product_id == product_id, Review.is_approved.is_(True))
    (total, average) = db.execute(
        select(func.count(Review.id), func.avg(Review.rating)).where(*conditions)
    ).one()
    reviews = db.scalars(
        select(Review)
        .where(*conditions)
        .order_by(Review.created_at.desc(), Review.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .options(selectinload(Review.user))
    )
    items = [
        ReviewResponse(
            id=review.id,
            rating=review.rating,
            title=review.title,
            body=review.body,
            author=review.user.first_name.strip() or "ByteDesk customer",
            created_at=review.created_at,
        )
        for review in reviews
    ]
    return ReviewPage(
        items=items,
        average_rating=Decimal(average).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        if average is not None
        else None,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size),
    )


def create(db: Session, user_id: int, data: ReviewCreate) -> Review:
    active_product(db, data.product_id)
    review = Review(
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        is_approved=False,
        **data.model_dump(),
    )
    db.add(review)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        name = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if name == "unique_user_product_review":
            raise StoreError(
                409, "You have already reviewed this product.", code="duplicate_review"
            ) from None
        raise
    return review


def own_review(db: Session, user_id: int, product_id: int) -> Review | None:
    active_product(db, product_id)
    return db.scalar(
        select(Review).where(Review.user_id == user_id, Review.product_id == product_id)
    )
