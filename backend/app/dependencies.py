from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import User
from .services.auth import authenticate
from .services.errors import StoreError


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


DatabaseSession = Annotated[Session, Depends(get_db)]
bearer = HTTPBearer(auto_error=False)


def current_user(
    db: DatabaseSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    if credentials is None:
        raise StoreError(
            401,
            "Please sign in to continue.",
            headers={"WWW-Authenticate": "Bearer"},
            code="authentication_required",
        )
    return authenticate(db, credentials.credentials)


CurrentUser = Annotated[User, Depends(current_user)]
