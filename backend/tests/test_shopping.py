from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.models import Cart, CartItem, Order, Product, User
from app.services.auth import issue_token


@pytest.fixture
def shopper(db, catalog):
    user = User(
        username=f"customer_{uuid4().hex[:12]}",
        email=f"{uuid4().hex}@example.com",
        password="!",
        date_joined=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    return {
        "user": user,
        "headers": {"Authorization": "Bearer " + issue_token(user).access_token},
        "catalog": catalog,
        "product": catalog["products"][0],
    }


@pytest.fixture
def shipping():
    return {
        "checkout_key": str(uuid4()),
        "shipping_name": "Casey Morgan",
        "shipping_address": "42 Demo Street",
        "shipping_city": "Portland",
        "shipping_postal_code": "97201",
        "shipping_country": "United States",
    }


def add(client, shopper, quantity=1, product=None):
    return client.post(
        "/api/cart/items",
        headers=shopper["headers"],
        json={"product_id": (product or shopper["product"]).id, "quantity": quantity},
    )


def place(client, shopper, shipping):
    return client.post("/api/orders", headers=shopper["headers"], json=shipping)


def test_empty_cart_and_wishlist_do_not_create_rows(client, db, shopper):
    data = client.get("/api/cart", headers=shopper["headers"]).json()
    assert data["items"] == [] and Decimal(data["total"]) == 0
    assert Decimal(data["shipping"]) == 0
    assert client.get("/api/wishlist", headers=shopper["headers"]).json() == {
        "items": []
    }
    assert db.scalar(select(Cart).where(Cart.user_id == shopper["user"].id)) is None


def test_cart_add_merge_edit_and_remove(client, db, shopper):
    first = add(client, shopper)
    assert first.status_code == 200, first.text
    item_id = first.json()["items"][0]["id"]
    merged = add(client, shopper).json()
    assert len(merged["items"]) == 1 and merged["item_count"] == 2
    assert Decimal(merged["subtotal"]) == 100 and Decimal(merged["shipping"]) == 0
    edited = client.patch(
        f"/api/cart/items/{item_id}", headers=shopper["headers"], json={"quantity": 1}
    )
    assert edited.status_code == 200
    assert Decimal(edited.json()["subtotal"]) == 50
    assert Decimal(edited.json()["shipping"]) == 8
    assert Decimal(edited.json()["total"]) == 58
    removed = client.delete(f"/api/cart/items/{item_id}", headers=shopper["headers"])
    assert removed.status_code == 200 and removed.json()["items"] == []
    assert Decimal(removed.json()["shipping"]) == 0
    assert (
        db.scalar(
            select(func.count())
            .select_from(CartItem)
            .join(Cart)
            .where(Cart.user_id == shopper["user"].id)
        )
        == 0
    )


@pytest.mark.parametrize("quantity", [0, -1, 10001, 1.5, True, "2"])
def test_invalid_cart_quantity(client, shopper, quantity):
    assert add(client, shopper, quantity).status_code == 422


def test_stock_limits_and_unavailable_products(client, db, shopper):
    failure = add(client, shopper, 9)
    assert failure.status_code == 409
    assert failure.json()["code"] == "insufficient_stock"
    assert failure.json()["params"] == {"product": shopper["product"].name, "stock": 8}
    assert (
        add(client, shopper, product=shopper["catalog"]["products"][2]).status_code
        == 409
    )
    assert (
        add(client, shopper, product=shopper["catalog"]["products"][3]).status_code
        == 409
    )
    assert add(client, shopper, 8).status_code == 200
    assert add(client, shopper, 1).status_code == 409
    current = client.get("/api/cart", headers=shopper["headers"]).json()
    assert current["item_count"] == 8
    assert db.get(Product, shopper["product"].id).stock_quantity == 8


def test_client_prices_and_owner_are_rejected(client, shopper):
    for field in ["price", "subtotal", "user_id"]:
        result = client.post(
            "/api/cart/items",
            headers=shopper["headers"],
            json={"product_id": shopper["product"].id, field: 1},
        )
        assert result.status_code == 422


def test_cart_ownership(client, db, shopper):
    line = add(client, shopper).json()["items"][0]
    other = User(
        username="other_" + uuid4().hex[:10],
        email=f"{uuid4().hex}@example.com",
        password="!",
        date_joined=datetime.now(timezone.utc),
    )
    db.add(other)
    db.commit()
    headers = {"Authorization": "Bearer " + issue_token(other).access_token}
    assert client.get("/api/cart", headers=headers).json()["items"] == []
    assert (
        client.patch(
            f"/api/cart/items/{line['id']}", headers=headers, json={"quantity": 2}
        ).status_code
        == 404
    )
    assert (
        client.delete(f"/api/cart/items/{line['id']}", headers=headers).status_code
        == 404
    )
    assert client.get("/api/cart", headers=shopper["headers"]).json()["item_count"] == 1


def test_wishlist_is_unique_and_move_is_atomic(client, db, shopper):
    body = {"product_id": shopper["product"].id}
    for _ in range(2):
        result = client.post(
            "/api/wishlist/items", headers=shopper["headers"], json=body
        )
        assert result.status_code == 200 and len(result.json()["items"]) == 1
    assert add(client, shopper, 8).status_code == 200
    result = client.post(
        f"/api/wishlist/items/{body['product_id']}/move-to-cart",
        headers=shopper["headers"],
    )
    assert result.status_code == 409
    assert (
        len(client.get("/api/wishlist", headers=shopper["headers"]).json()["items"])
        == 1
    )
    line = client.get("/api/cart", headers=shopper["headers"]).json()["items"][0]
    client.patch(
        f"/api/cart/items/{line['id']}",
        headers=shopper["headers"],
        json={"quantity": 1},
    )
    moved = client.post(
        f"/api/wishlist/items/{body['product_id']}/move-to-cart",
        headers=shopper["headers"],
    )
    assert moved.status_code == 200 and moved.json()["item_count"] == 2
    assert client.get("/api/wishlist", headers=shopper["headers"]).json()["items"] == []


def test_wishlist_can_save_out_of_stock_and_remove(client, shopper):
    product = shopper["catalog"]["products"][2]
    saved = client.post(
        "/api/wishlist/items",
        headers=shopper["headers"],
        json={"product_id": product.id},
    )
    assert saved.status_code == 200 and not saved.json()["items"][0]["available"]
    assert (
        client.post(
            f"/api/wishlist/items/{product.id}/move-to-cart", headers=shopper["headers"]
        ).status_code
        == 409
    )
    assert (
        client.delete(
            f"/api/wishlist/items/{product.id}", headers=shopper["headers"]
        ).json()["items"]
        == []
    )


def test_checkout_server_totals_snapshots_inventory_and_cart(
    client, db, shopper, shipping
):
    add(client, shopper, 2)
    before = shopper["product"].stock_quantity
    response = place(client, shopper, shipping)
    assert response.status_code == 201, response.text
    order = response.json()
    assert order["status"] == "pending"
    assert Decimal(order["subtotal"]) == 100 and Decimal(order["shipping"]) == 0
    assert Decimal(order["total"]) == 100
    assert order["items"][0]["quantity"] == 2
    assert order["items"][0]["product_name"] == shopper["product"].name
    assert Decimal(order["items"][0]["unit_price"]) == 50
    assert db.get(Product, shopper["product"].id).stock_quantity == before - 2
    assert client.get("/api/cart", headers=shopper["headers"]).json()["items"] == []
    product = db.get(Product, shopper["product"].id)
    product.name = "Changed name"
    product.price = Decimal("999.00")
    db.commit()
    historical = client.get(
        f"/api/orders/{order['id']}", headers=shopper["headers"]
    ).json()
    assert historical["items"][0]["product_name"] != product.name
    assert Decimal(historical["items"][0]["unit_price"]) == 50
    assert Decimal(historical["total"]) == 100


def test_checkout_retry_returns_same_order_and_preserves_new_cart(
    client, db, shopper, shipping
):
    add(client, shopper)
    first = place(client, shopper, shipping)
    assert first.status_code == 201, first.text
    add(client, shopper)
    replay = place(client, shopper, shipping)
    assert replay.status_code == 201 and replay.json()["id"] == first.json()["id"]
    assert client.get("/api/cart", headers=shopper["headers"]).json()["item_count"] == 1
    assert db.get(Product, shopper["product"].id).stock_quantity == 7
    assert (
        db.scalar(
            select(func.count())
            .select_from(Order)
            .where(Order.user_id == shopper["user"].id)
        )
        == 1
    )


def test_stock_change_blocks_entire_checkout(client, db, shopper, shipping):
    add(client, shopper, 2)
    other = shopper["catalog"]["products"][1]
    add(client, shopper, 1, other)
    product = db.get(Product, shopper["product"].id)
    product.stock_quantity = 1
    db.commit()
    assert place(client, shopper, shipping).status_code == 409
    assert db.get(Product, other.id).stock_quantity == 3
    assert client.get("/api/cart", headers=shopper["headers"]).json()["item_count"] == 3
    assert (
        db.scalar(
            select(func.count())
            .select_from(Order)
            .where(Order.user_id == shopper["user"].id)
        )
        == 0
    )
    assert not client.get("/api/cart", headers=shopper["headers"]).json()["items"][0][
        "available"
    ]


def test_inactive_product_blocks_checkout(client, db, shopper, shipping):
    add(client, shopper)
    product = db.get(Product, shopper["product"].id)
    product.is_active = False
    db.commit()
    assert place(client, shopper, shipping).status_code == 409
    assert db.get(Product, product.id).stock_quantity == 8


def test_empty_checkout_and_invalid_shipping(client, shopper, shipping):
    assert place(client, shopper, shipping).status_code == 409
    add(client, shopper)
    assert (
        place(client, shopper, {**shipping, "shipping_address": "  "}).status_code
        == 422
    )
    assert place(client, shopper, {**shipping, "total": "0.01"}).status_code == 422
    assert (
        place(client, shopper, {**shipping, "checkout_key": "bad"}).status_code == 422
    )


def test_order_ownership_pagination_and_status(client, db, shopper, shipping):
    add(client, shopper)
    created = place(client, shopper, shipping).json()
    other = User(
        username="other_" + uuid4().hex[:10],
        email=f"{uuid4().hex}@example.com",
        password="!",
        date_joined=datetime.now(timezone.utc),
    )
    db.add(other)
    db.commit()
    other_headers = {"Authorization": "Bearer " + issue_token(other).access_token}
    assert (
        client.get(f"/api/orders/{created['id']}", headers=other_headers).status_code
        == 404
    )
    assert client.get("/api/orders", headers=other_headers).json()["total"] == 0
    listing = client.get("/api/orders?page_size=1", headers=shopper["headers"]).json()
    assert listing["total"] == 1 and listing["items"][0]["id"] == created["id"]
    assert (
        client.get("/api/orders?page=2&page_size=1", headers=shopper["headers"]).json()[
            "items"
        ]
        == []
    )
    order = db.get(Order, created["id"])
    order.status = "shipped"
    db.commit()
    assert (
        client.get(f"/api/orders/{created['id']}", headers=shopper["headers"]).json()[
            "status"
        ]
        == "shipped"
    )
    assert (
        client.get("/api/orders?page=0", headers=shopper["headers"]).status_code == 422
    )


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/api/cart"),
        ("POST", "/api/cart/items"),
        ("GET", "/api/wishlist"),
        ("POST", "/api/wishlist/items"),
        ("GET", "/api/orders"),
        ("POST", "/api/orders"),
        ("GET", "/api/orders/1"),
    ],
)
def test_shopping_requires_authentication(client, method, path):
    assert client.request(method, path, json={}).status_code == 401


def test_missing_cart_product(client, shopper):
    response = client.post(
        "/api/cart/items",
        headers=shopper["headers"],
        json={"product_id": 9223372036854775806},
    )
    assert response.status_code == 404


def test_commit_failure_rolls_back_order_inventory_and_cart(
    client, db, shopper, shipping, monkeypatch
):
    from sqlalchemy.exc import OperationalError

    add(client, shopper, 2)

    def failed_commit():
        raise OperationalError("commit", {}, Exception("simulated transaction failure"))

    with monkeypatch.context() as patch:
        patch.setattr(db, "commit", failed_commit)
        result = place(client, shopper, shipping)
    assert result.status_code == 503
    db.expire_all()
    assert db.get(Product, shopper["product"].id).stock_quantity == 8
    assert client.get("/api/cart", headers=shopper["headers"]).json()["item_count"] == 2
    assert (
        db.scalar(
            select(func.count())
            .select_from(Order)
            .where(Order.user_id == shopper["user"].id)
        )
        == 0
    )


def test_wishlist_is_private(client, db, shopper):
    product_id = shopper["product"].id
    assert (
        client.post(
            "/api/wishlist/items",
            headers=shopper["headers"],
            json={"product_id": product_id},
        ).status_code
        == 200
    )
    other = User(
        username="other_" + uuid4().hex[:10],
        email=f"{uuid4().hex}@example.com",
        password="!",
        date_joined=datetime.now(timezone.utc),
    )
    db.add(other)
    db.commit()
    headers = {"Authorization": "Bearer " + issue_token(other).access_token}
    assert client.get("/api/wishlist", headers=headers).json()["items"] == []
    assert (
        client.delete(f"/api/wishlist/items/{product_id}", headers=headers).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/wishlist/items/{product_id}/move-to-cart", headers=headers
        ).status_code
        == 404
    )
    assert (
        len(client.get("/api/wishlist", headers=shopper["headers"]).json()["items"])
        == 1
    )
