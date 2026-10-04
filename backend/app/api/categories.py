from typing import Annotated, Literal

from fastapi import APIRouter, Path

from ..dependencies import DatabaseSession
from ..schemas.category import CategoryResponse
from ..schemas.common import ErrorResponse
from ..services import taxonomy

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: DatabaseSession, lang: Literal["en", "tr"] = "en"):
    return [
        taxonomy.localized_category(category, lang)
        for category in taxonomy.list_categories(db)
    ]


@router.get(
    "/{slug}",
    response_model=CategoryResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_category(
    db: DatabaseSession,
    slug: Annotated[str, Path(max_length=50)],
    lang: Literal["en", "tr"] = "en",
):
    return taxonomy.localized_category(taxonomy.get_category(db, slug), lang)
