from typing import Annotated

from fastapi import APIRouter, Path

from ..dependencies import DatabaseSession
from ..schemas.brand import BrandResponse
from ..schemas.common import ErrorResponse
from ..services import taxonomy

router = APIRouter(prefix="/api/brands", tags=["Brands"])


@router.get("", response_model=list[BrandResponse])
def list_brands(db: DatabaseSession):
    return taxonomy.list_brands(db)


@router.get(
    "/{slug}", response_model=BrandResponse, responses={404: {"model": ErrorResponse}}
)
def get_brand(db: DatabaseSession, slug: Annotated[str, Path(max_length=50)]):
    return taxonomy.get_brand(db, slug)
