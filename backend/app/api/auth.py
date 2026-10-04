from fastapi import APIRouter

from ..dependencies import CurrentUser, DatabaseSession
from ..schemas.auth import Login, MessageResponse, Registration, TokenResponse
from ..services import auth

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: Registration, db: DatabaseSession):
    return auth.register(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: Login, db: DatabaseSession):
    return auth.login(db, str(data.email), data.password)


@router.post("/logout", response_model=MessageResponse)
def logout(db: DatabaseSession, user: CurrentUser):
    auth.logout(db, user)
    return MessageResponse(detail="Signed out of all sessions.")
