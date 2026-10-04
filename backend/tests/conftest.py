"""PostgreSQL integration tests use savepoints and roll back all fixture data."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import engine
from app.dependencies import get_db
from app.main import app
from app.models import Brand, Category, Product, ProductImage, ProductSpecification


@pytest.fixture
def db():
    if get_settings().app_env != "development":
        pytest.fail("Catalog integration tests require APP_ENV=development")
    with engine.connect() as connection:
        outer = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            session.close()
            outer.rollback()


@pytest.fixture
def client(db):
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def catalog(db):
    marker = f"fixture-{uuid4().hex[:12]}"
    keyboards = Category(name=f"Fixture Keyboards {marker}", slug=f"{marker}-keys")
    audio = Category(name=f"Fixture Audio {marker}", slug=f"{marker}-audio")
    acme = Brand(name=f"Acme {marker}", slug=f"{marker}-acme")
    sonic = Brand(name=f"Sonic {marker}", slug=f"{marker}-sonic")
    db.add_all([keyboards, audio, acme, sonic])
    db.flush()
    now = datetime.now(timezone.utc)
    products = []
    for index, (name, price, stock, category, brand, active) in enumerate(
        [
            ("Alpha Keyboard", "50.00", 8, keyboards, acme, True),
            ("Beta Keyboard", "150.00", 3, keyboards, sonic, True),
            ("Gamma Headphones", "99.00", 0, audio, acme, True),
            ("Hidden Keyboard", "25.00", 10, keyboards, acme, False),
        ]
    ):
        product = Product(
            name=f"{marker} {name}",
            slug=f"{marker}-{index}",
            sku=f"{marker}-sku-{index}",
            description=f"{marker}-description-{index}",
            price=Decimal(price),
            stock_quantity=stock,
            category=category,
            brand=brand,
            is_active=active,
            created_at=now,
            updated_at=now,
        )
        db.add(product)
        products.append(product)
    db.flush()
    db.add_all(
        [
            ProductSpecification(product_id=products[0].id, key="Layout", value="75%"),
            ProductImage(
                product_id=products[0].id,
                url="/images/keyboard-back.jpg",
                alt_text="Back",
                position=2,
            ),
            ProductImage(
                product_id=products[0].id,
                url="/images/keyboard-front.jpg",
                alt_text="Front",
                position=1,
            ),
        ]
    )
    db.flush()
    return {
        "marker": marker,
        "products": products,
        "category": keyboards,
        "brand": acme,
    }
