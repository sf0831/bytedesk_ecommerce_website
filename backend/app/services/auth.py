from datetime import datetime, timedelta, timezone

import jwt
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import User
from ..schemas.auth import Registration, TokenResponse, UserProfile
from .errors import StoreError

hasher = PBKDF2PasswordHasher()
_dummy = hasher.encode("unused-random-verification-password", hasher.salt())


def issue_token(user: User) -> TokenResponse:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    seconds = settings.access_token_expire_minutes * 60
    token = jwt.encode(
        {
            "sub": str(user.id),
            "ver": user.auth_version,
            "iat": now,
            "exp": now + timedelta(seconds=seconds),
            "iss": "bytedesk",
            "aud": "bytedesk-store",
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return TokenResponse(
        access_token=token, expires_in=seconds, user=UserProfile.model_validate(user)
    )


def register(db: Session, data: Registration) -> TokenResponse:
    user = User(
        username=data.username,
        email=str(data.email).lower(),
        password=hasher.encode(data.password, hasher.salt()),
        first_name=data.first_name.strip(),
        last_name=data.last_name.strip(),
        date_joined=datetime.now(timezone.utc),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise StoreError(
            409,
            "An account with that email or username already exists.",
            code="account_exists",
        ) from None
    return issue_token(user)


def login(db: Session, email: str, password: str) -> TokenResponse:
    user = db.scalar(select(User).where(func.lower(User.email) == email.lower()))
    encoded = user.password if user else _dummy
    try:
        valid = hasher.verify(password, encoded)
    except (ValueError, TypeError):
        valid = False
    if not user or not valid or (not user.is_active):
        raise StoreError(
            401,
            "Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
            code="invalid_credentials",
        )
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    return issue_token(user)


def authenticate(db: Session, token: str) -> User:
    settings = get_settings()
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer="bytedesk",
            audience="bytedesk-store",
            options={"require": ["sub", "ver", "iat", "exp"]},
        )
        user = db.get(User, int(claims["sub"]))
        if not user or not user.is_active or user.auth_version != claims["ver"]:
            raise ValueError("Invalid session")
        return user
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise StoreError(
            401,
            "Your session has expired. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
            code="session_expired",
        ) from None


def logout(db: Session, user: User) -> None:
    db.execute(
        update(User)
        .where(User.id == user.id)
        .values(auth_version=User.auth_version + 1)
    )
    db.commit()
