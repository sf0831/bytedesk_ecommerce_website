from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from sqlalchemy import select

from app.config import get_settings
from app.models import User
from app.services.auth import hasher


@pytest.fixture
def account():
    suffix = uuid4().hex[:12]
    return {
        "username": f"member_{suffix}",
        "email": f"member_{suffix}@example.com",
        "password": "Test-password-482!",
        "first_name": "Sam",
        "last_name": "River",
    }


def register(client, account):
    response = client.post("/api/auth/register", json=account)
    assert response.status_code == 201, response.text
    return response.json()


def headers(data):
    return {"Authorization": f"Bearer {data['access_token']}"}


def test_registration_hashes_password_and_protects_profile(client, db, account):
    data = register(client, account)
    user = db.scalar(select(User).where(User.email == account["email"]))
    assert user.password != account["password"]
    assert hasher.verify(account["password"], user.password)
    assert not user.is_staff and not user.is_superuser
    assert user.password.startswith("pbkdf2_sha256$")
    profile = client.get("/api/users/me", headers=headers(data))
    assert profile.status_code == 200
    assert profile.json()["first_name"] == "Sam"
    assert set(profile.json()) == {
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "date_joined",
    }


@pytest.mark.parametrize(
    "changes",
    [
        {"password": "short"},
        {"email": "invalid"},
        {"username": "bad space"},
        {"is_staff": True},
        {"is_superuser": True},
        {"auth_version": 10},
    ],
)
def test_registration_validation(client, account, changes):
    assert (
        client.post("/api/auth/register", json={**account, **changes}).status_code
        == 422
    )


@pytest.mark.parametrize("field", ["email", "username"])
def test_duplicate_registration(client, account, field):
    register(client, account)
    duplicate = {
        **account,
        "username": "other_" + uuid4().hex[:10],
        "email": f"{uuid4().hex}@example.com",
    }
    duplicate[field] = account[field].upper() if field == "email" else account[field]
    assert client.post("/api/auth/register", json=duplicate).status_code == 409
    assert client.get("/api/products").status_code == 200


def test_login_case_insensitive_email(client, account):
    register(client, account)
    result = client.post(
        "/api/auth/login",
        json={"email": account["email"].upper(), "password": account["password"]},
    )
    assert result.status_code == 200
    assert (
        client.get("/api/users/me", headers=headers(result.json())).status_code == 200
    )


def test_invalid_credentials_and_inactive_user(client, db, account):
    register(client, account)
    for email, password in [
        (account["email"], "wrong"),
        ("missing@example.com", "wrong"),
    ]:
        result = client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        assert result.status_code == 401
        assert result.json()["detail"] == "Invalid email or password."
    user = db.scalar(select(User).where(User.email == account["email"]))
    user.is_active = False
    db.commit()
    assert (
        client.post(
            "/api/auth/login",
            json={"email": account["email"], "password": account["password"]},
        ).status_code
        == 401
    )


@pytest.mark.parametrize("authorization", [None, "Bearer invalid", "Basic invalid"])
def test_profile_requires_authentication(client, authorization):
    response = client.get(
        "/api/users/me",
        headers={"Authorization": authorization} if authorization else {},
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    "change", ["expired", "signature", "audience", "issuer", "missing", "non_numeric"]
)
def test_invalid_jwt_is_rejected(client, account, change):
    data = register(client, account)
    settings = get_settings()
    claims = jwt.decode(
        data["access_token"],
        settings.jwt_secret_key,
        algorithms=["HS256"],
        audience="bytedesk-store",
    )
    secret = settings.jwt_secret_key
    if change == "expired":
        claims["exp"] = datetime.now(timezone.utc) - timedelta(seconds=1)
    if change == "signature":
        secret = "wrong-secret-key-with-at-least-32-characters"
    if change == "audience":
        claims["aud"] = "other"
    if change == "issuer":
        claims["iss"] = "other"
    if change == "missing":
        del claims["ver"]
    if change == "non_numeric":
        claims["sub"] = "not-an-id"
    token = jwt.encode(claims, secret, algorithm="HS256")
    assert (
        client.get(
            "/api/users/me", headers={"Authorization": f"Bearer {token}"}
        ).status_code
        == 401
    )


def test_logout_revokes_all_tokens_and_can_login_again(client, account):
    first = register(client, account)
    second = client.post(
        "/api/auth/login",
        json={"email": account["email"], "password": account["password"]},
    ).json()
    assert client.post("/api/auth/logout", headers=headers(first)).status_code == 200
    for data in [first, second]:
        assert client.get("/api/users/me", headers=headers(data)).status_code == 401
    fresh = client.post(
        "/api/auth/login",
        json={"email": account["email"], "password": account["password"]},
    ).json()
    assert client.get("/api/users/me", headers=headers(fresh)).status_code == 200


def test_disabled_account_token_revoked(client, db, account):
    data = register(client, account)
    user = db.get(User, data["user"]["id"])
    user.is_active = False
    db.commit()
    assert client.get("/api/users/me", headers=headers(data)).status_code == 401
