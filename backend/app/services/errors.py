from fastapi import HTTPException


class StoreError(HTTPException):
    """Stable public code and safe interpolation data, alongside an English detail."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        *,
        code: str,
        params: dict | None = None,
        headers: dict | None = None,
    ):
        super().__init__(status_code, detail, headers)
        self.code = code
        self.params = params or {}


class NotFoundError(StoreError):
    def __init__(self, detail: str, *, code: str):
        super().__init__(404, detail, code=code)
