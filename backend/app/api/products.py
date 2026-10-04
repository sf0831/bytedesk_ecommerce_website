from typing import Annotated, Literal

from fastapi import APIRouter, Path, Query

from ..dependencies import DatabaseSession
from ..schemas.common import ErrorResponse
from ..schemas.product import ProductDetail, ProductFilters, ProductPage
from ..services import product as service

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=ProductPage, summary="Search and filter active products")
def list_products(db: DatabaseSession, filters: Annotated[ProductFilters, Query()]):
    return service.list_products(db, filters)


@router.get(
    "/{slug}",
    response_model=ProductDetail,
    responses={404: {"model": ErrorResponse}},
    summary="Product details, images and specifications",
)
def get_product(
    db: DatabaseSession,
    slug: Annotated[str, Path(max_length=220)],
    lang: Literal["en", "tr"] = "en",
):
    return service.get_product(db, slug, lang)
