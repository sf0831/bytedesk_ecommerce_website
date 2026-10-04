"""Real PostgreSQL transactions verify row-lock behavior, beyond savepoint tests."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal
from threading import Barrier
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import delete, func, select

from app.config import get_settings
from app.database import SessionLocal
from app.models import Brand, Cart, CartItem, Category, Order, OrderItem, Product, User
from app.schemas.order import CheckoutRequest
from app.services.order import checkout


@pytest.fixture
def concurrent_store():
    assert get_settings().app_env == "development"
    marker = "concurrency-" + uuid4().hex
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)
        category = Category(name=marker, slug=marker)
        brand = Brand(name=marker, slug=marker)
        db.add_all([category, brand])
        db.flush()
        product = Product(
            name=marker,
            slug=marker,
            sku=marker,
            description="Concurrency fixture",
            price=Decimal("25.00"),
            stock_quantity=1,
            category_id=category.id,
            brand_id=brand.id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        db.add(product)
        db.flush()
        users = []
        carts = []
        for index in range(2):
            user = User(
                username=f"{marker}-{index}",
                email=f"{marker}-{index}@example.com",
                password="!",
                date_joined=now,
            )
            db.add(user)
            db.flush()
            cart = Cart(user_id=user.id, created_at=now, updated_at=now)
            db.add(cart)
            db.flush()
            db.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=1))
            users.append(user.id)
            carts.append(cart.id)
        db.commit()
        ids = {
            "users": users,
            "carts": carts,
            "product": product.id,
            "category": category.id,
            "brand": brand.id,
        }
    try:
        yield ids
    finally:
        # Only delete committed records created by this fixture, never seed data.
        with SessionLocal() as db:
            orders = select(Order.id).where(Order.user_id.in_(ids["users"]))
            db.execute(delete(OrderItem).where(OrderItem.order_id.in_(orders)))
            db.execute(delete(Order).where(Order.user_id.in_(ids["users"])))
            db.execute(delete(CartItem).where(CartItem.cart_id.in_(ids["carts"])))
            db.execute(delete(Cart).where(Cart.id.in_(ids["carts"])))
            db.execute(delete(User).where(User.id.in_(ids["users"])))
            db.execute(delete(Product).where(Product.id == ids["product"]))
            db.execute(delete(Category).where(Category.id == ids["category"]))
            db.execute(delete(Brand).where(Brand.id == ids["brand"]))
            db.commit()


def checkout_data(key=None):
    return CheckoutRequest(
        checkout_key=key or uuid4(),
        shipping_name="Demo Customer",
        shipping_address="42 Demo Street",
        shipping_city="Portland",
        shipping_postal_code="97201",
        shipping_country="United States",
    )


def test_two_customers_cannot_buy_last_unit(concurrent_store):
    barrier = Barrier(2)

    def buy(user_id):
        with SessionLocal() as db:
            barrier.wait(timeout=10)
            try:
                return ("ordered", checkout(db, user_id, checkout_data()).id)
            except HTTPException as exc:
                return ("rejected", exc.status_code)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(buy, concurrent_store["users"]))
    assert sorted(result[0] for result in results) == ["ordered", "rejected"]
    assert [value for kind, value in results if kind == "rejected"] == [409]
    with SessionLocal() as db:
        assert db.get(Product, concurrent_store["product"]).stock_quantity == 0
        assert (
            db.scalar(
                select(func.count())
                .select_from(Order)
                .where(Order.user_id.in_(concurrent_store["users"]))
            )
            == 1
        )
        assert (
            db.scalar(
                select(func.count())
                .select_from(CartItem)
                .where(CartItem.cart_id.in_(concurrent_store["carts"]))
            )
            == 1
        )


def test_concurrent_checkout_retries_create_one_order(concurrent_store):
    barrier = Barrier(2)
    user_id = concurrent_store["users"][0]
    data = checkout_data()

    def buy(_):
        with SessionLocal() as db:
            barrier.wait(timeout=10)
            return checkout(db, user_id, data).id

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(buy, range(2)))
    assert results[0] == results[1]
    with SessionLocal() as db:
        assert db.get(Product, concurrent_store["product"]).stock_quantity == 0
        assert (
            db.scalar(
                select(func.count()).select_from(Order).where(Order.user_id == user_id)
            )
            == 1
        )
