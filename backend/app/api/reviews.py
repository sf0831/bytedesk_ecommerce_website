from typing import Annotated

from fastapi import APIRouter, Query

from ..dependencies import CurrentUser, DatabaseSession
from ..schemas.review import ReviewCreate, ReviewPage, ReviewSubmission
from ..services import review

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])


@router.get("", response_model=ReviewPage)
def listing(
    db: DatabaseSession,
    product_id: Annotated[int, Query(gt=0, le=9223372036854775807)],
    page: Annotated[int, Query(ge=1, le=2147483647)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return review.listing(db, product_id, page, page_size)


@router.post("", response_model=ReviewSubmission, status_code=201)
def create(data: ReviewCreate, db: DatabaseSession, user: CurrentUser):
    return review.create(db, user.id, data)


@router.get("/me", response_model=ReviewSubmission | None)
def own(
    db: DatabaseSession,
    user: CurrentUser,
    product_id: Annotated[int, Query(gt=0, le=9223372036854775807)],
):
    return review.own_review(db, user.id, product_id)
