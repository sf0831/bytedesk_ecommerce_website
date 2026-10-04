from typing import Literal

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
    params: dict = {}


class HealthResponse(BaseModel):
    status: Literal["ok", "unavailable"]
    database: Literal["connected", "unavailable"]
