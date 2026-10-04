from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..dependencies import DatabaseSession
from ..schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/api/health",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse}},
)
def health(db: DatabaseSession):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "database": "unavailable"},
        )
    return HealthResponse(status="ok", database="connected")
