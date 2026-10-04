from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.models import Review, User
from app.services.auth import issue_token


@pytest.fixture
def reviewer(db, catalog):
    user = User(
        username="reviewer_" + uuid4().hex[:12],
        email=f"{uuid4().hex}@example.com",
        password="!",
        first_name="Casey",
        date_joined=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    return {
        "user": user,
        "headers": {"Authorization": "Bearer " + issue_token(user).access_token},
        "product": catalog["products"][0],
        "catalog": catalog,
    }


@pytest.fixture
def review_data(reviewer):
    return {
        "product_id": reviewer["product"].id,
        "rating": 4,
        "title": "Comfortable everyday keyboard",
        "body": "The keys feel comfortable during a full day of typing.",
    }


def test_review_creation_pending_and_private(client, db, reviewer, review_data):
    created = client.post("/api/reviews", headers=reviewer["headers"], json=review_data)
    assert created.status_code == 201, created.text
    assert not created.json()["is_approved"]
    assert db.get(Review, created.json()["id"]).user_id == reviewer["user"].id
    public = client.get(
        "/api/reviews", params={"product_id": reviewer["product"].id}
    ).json()
    assert (
        public["items"] == []
        and public["total"] == 0
        and public["average_rating"] is None
    )
    own = client.get(
        "/api/reviews/me",
        headers=reviewer["headers"],
        params={"product_id": reviewer["product"].id},
    )
    assert own.status_code == 200 and own.json()["id"] == created.json()["id"]
    assert "user_id" not in own.json()


@pytest.mark.parametrize(
    "changes",
    [
        {"rating": 0},
        {"rating": 6},
        {"rating": True},
        {"rating": 2.5},
        {"rating": "5"},
        {"title": "  "},
        {"body": "short"},
        {"body": " " * 20},
        {"title": "a" * 161},
        {"body": "a" * 5001},
        {"is_approved": True},
        {"user_id": 1},
    ],
)
def test_review_validation(client, reviewer, review_data, changes):
    assert (
        client.post(
            "/api/reviews", headers=reviewer["headers"], json={**review_data, **changes}
        ).status_code
        == 422
    )


def test_one_review_per_customer_including_pending(client, db, reviewer, review_data):
    first = client.post("/api/reviews", headers=reviewer["headers"], json=review_data)
    assert first.status_code == 201
    assert (
        client.post(
            "/api/reviews", headers=reviewer["headers"], json=review_data
        ).status_code
        == 409
    )
    stored = db.get(Review, first.json()["id"])
    stored.is_approved = True
    db.commit()
    assert (
        client.post(
            "/api/reviews", headers=reviewer["headers"], json=review_data
        ).status_code
        == 409
    )
    assert (
        len(
            list(
                db.scalars(select(Review).where(Review.user_id == reviewer["user"].id))
            )
        )
        == 1
    )


def test_public_ratings_pagination_and_moderation(client, db, reviewer, review_data):
    product_id = reviewer["product"].id
    now = datetime.now(timezone.utc)
    for index, rating in enumerate([5, 2, 1]):
        user = User(
            username="other_" + uuid4().hex[:12],
            email=f"{uuid4().hex}@example.com",
            password="!",
            date_joined=now,
        )
        db.add(user)
        db.flush()
        db.add(
            Review(
                user_id=user.id,
                product_id=product_id,
                rating=rating,
                title=f"Review {index}",
                body="A useful everyday workspace tool.",
                is_approved=index < 2,
                created_at=now,
            )
        )
    db.commit()
    public = client.get(
        "/api/reviews", params={"product_id": product_id, "page_size": 1}
    ).json()
    assert (
        public["total"] == 2
        and public["average_rating"] == "3.5"
        and public["total_pages"] == 2
    )
    assert len(public["items"]) == 1
    assert public["items"][0]["author"] == "ByteDesk customer"
    assert set(public["items"][0]) == {
        "id",
        "rating",
        "title",
        "body",
        "author",
        "created_at",
    }
    second = client.get(
        "/api/reviews", params={"product_id": product_id, "page_size": 1, "page": 2}
    ).json()
    assert second["items"][0]["id"] != public["items"][0]["id"]
    stored = db.get(Review, public["items"][0]["id"])
    stored.is_approved = False
    db.commit()
    assert (
        client.get("/api/reviews", params={"product_id": product_id}).json()["total"]
        == 1
    )


def test_own_review_is_scoped_to_user(client, db, reviewer, review_data):
    client.post("/api/reviews", headers=reviewer["headers"], json=review_data)
    other = User(
        username="other_" + uuid4().hex[:12],
        email=f"{uuid4().hex}@example.com",
        password="!",
        date_joined=datetime.now(timezone.utc),
    )
    db.add(other)
    db.commit()
    response = client.get(
        "/api/reviews/me",
        headers={"Authorization": "Bearer " + issue_token(other).access_token},
        params={"product_id": reviewer["product"].id},
    )
    assert response.status_code == 200 and response.json() is None


def test_missing_and_inactive_products(client, reviewer, review_data):
    for product_id in [9223372036854775806, reviewer["catalog"]["products"][3].id]:
        assert (
            client.get("/api/reviews", params={"product_id": product_id}).status_code
            == 404
        )
        assert (
            client.post(
                "/api/reviews",
                headers=reviewer["headers"],
                json={**review_data, "product_id": product_id},
            ).status_code
            == 404
        )


def test_review_authentication_and_pagination_validation(client, reviewer, review_data):
    assert client.post("/api/reviews", json=review_data).status_code == 401
    assert (
        client.get(
            "/api/reviews/me", params={"product_id": reviewer["product"].id}
        ).status_code
        == 401
    )
    for params in [{"page": 0}, {"page_size": 101}, {"product_id": 0}]:
        assert (
            client.get(
                "/api/reviews", params={"product_id": reviewer["product"].id, **params}
            ).status_code
            == 422
        )
