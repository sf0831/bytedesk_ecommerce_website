from fastapi import APIRouter

from ..dependencies import CurrentUser
from ..schemas.auth import UserProfile

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
def profile(user: CurrentUser):
    return user
