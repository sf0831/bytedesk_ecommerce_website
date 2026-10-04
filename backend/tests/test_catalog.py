import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

from app.database import Base, engine
from app.dependencies import get_db
from app.main import app


def test_listing_returns_active_products_and_money(client, catalog):
    response = client.get("/api/products", params={"search": catalog["marker"]})
    assert response.status_code == 200
    page = response.json()
    assert page["total"] == 3
    assert page["page"] == 1
    assert page["total_pages"] == 1
    assert {item["slug"] for item in page["items"]} == {
        p.slug for p in catalog["products"][:3]
    }
    assert page["items"][0]["price"] == "50.00"
    assert page["items"][0]["category"]["slug"] == catalog["category"].slug


def test_combined_filters_are_intersected(client, catalog):
    response = client.get(
        "/api/products",
        params={
            "search": catalog["marker"],
            "category": catalog["category"].slug,
            "brand": catalog["brand"].slug,
            "min_price": "50",
            "max_price": "50",
        },
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["slug"] == catalog["products"][0].slug


@pytest.mark.parametrize("field", ["name", "sku", "description", "brand", "category"])
def test_search_fields_case_insensitive(client, catalog, field):
    product = catalog["products"][0]
    searches = {
        "name": (product.name, 1),
        "sku": (product.sku, 1),
        "description": (product.description, 1),
        "brand": (catalog["brand"].name, 2),
        "category": (catalog["category"].name, 2),
    }
    search, expected = searches[field]
    response = client.get("/api/products", params={"search": search.upper()})
    assert response.status_code == 200
    assert response.json()["total"] == expected


@pytest.mark.parametrize("search", ["%", "_", "' OR 1=1 --"])
def test_search_special_characters_are_literal(client, catalog, search):
    response = client.get(
        "/api/products", params={"search": search, "category": catalog["category"].slug}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0


@pytest.mark.parametrize(
    "sort,expected",
    [
        ("price_asc", ["50.00", "99.00", "150.00"]),
        ("price_desc", ["150.00", "99.00", "50.00"]),
    ],
)
def test_price_sort(client, catalog, sort, expected):
    page = client.get(
        "/api/products", params={"search": catalog["marker"], "sort": sort}
    ).json()
    assert [item["price"] for item in page["items"]] == expected


def test_pagination_stable_and_empty_page(client, catalog):
    parameters = {"search": catalog["marker"], "page_size": 2, "sort": "newest"}
    first = client.get("/api/products", params=parameters).json()
    second = client.get("/api/products", params={**parameters, "page": 2}).json()
    assert first["total"] == second["total"] == 3
    assert first["total_pages"] == 2
    assert len(first["items"]) == 2
    assert len(second["items"]) == 1
    assert not {p["id"] for p in first["items"]} & {p["id"] for p in second["items"]}
    assert (
        client.get("/api/products", params={**parameters, "page": 5}).json()["items"]
        == []
    )


def test_product_detail_includes_images_specs_and_stock(client, catalog):
    response = client.get(f"/api/products/{catalog['products'][0].slug}")
    assert response.status_code == 200
    detail = response.json()
    assert detail["specifications"] == [{"key": "Layout", "value": "75%"}]
    assert [image["alt_text"] for image in detail["images"]] == ["Front", "Back"]
    assert detail["in_stock"] is True
    out_of_stock = client.get(f"/api/products/{catalog['products'][2].slug}").json()
    assert out_of_stock["in_stock"] is False
    assert out_of_stock["stock_quantity"] == 0


def test_hidden_and_missing_products_are_not_public(client, catalog):
    for slug in (catalog["products"][3].slug, "nonexistent-product"):
        response = client.get(f"/api/products/{slug}")
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Product not found",
            "code": "product_not_found",
            "params": {},
        }


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page": 10**30},
        {"page_size": 0},
        {"page_size": 101},
        {"sort": "invalid"},
        {"min_price": -1},
        {"min_price": 100, "max_price": 50},
        {"max_price": "NaN"},
        {"min_price": "1.234"},
        {"search": "x" * 201},
        {"unexpected": "value"},
    ],
)
def test_invalid_filters_return_422(client, params):
    assert client.get("/api/products", params=params).status_code == 422


@pytest.mark.parametrize("kind", ["categories", "brands"])
def test_taxonomy_endpoints(client, catalog, kind):
    entity = catalog["category"] if kind == "categories" else catalog["brand"]
    listing = client.get(f"/api/{kind}")
    assert listing.status_code == 200
    assert any(item["slug"] == entity.slug for item in listing.json())
    assert client.get(f"/api/{kind}/{entity.slug}").json()["id"] == entity.id
    assert client.get(f"/api/{kind}/does-not-exist").status_code == 404


def test_health_and_openapi_documentation(client):
    assert client.get("/api/health").json() == {"status": "ok", "database": "connected"}
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(path).status_code == 200
    schema = client.get("/openapi.json").json()
    endpoint = schema["paths"]["/api/products"]["get"]
    assert "requestBody" not in endpoint
    assert {p["name"] for p in endpoint["parameters"]} >= {
        "search",
        "category",
        "brand",
        "min_price",
        "max_price",
        "sort",
        "page",
        "page_size",
    }
    assert "ProductPage" in schema["components"]["schemas"]


def test_database_failure_is_safe(client):
    class BrokenDatabase:
        def execute(self, *args, **kwargs):
            raise OperationalError(
                "secret internal query", {}, Exception("internal password")
            )

        scalar = execute

    app.dependency_overrides[get_db] = lambda: BrokenDatabase()
    response = client.get("/api/products")
    assert response.status_code == 503
    assert "internal" not in response.text
    assert client.get("/api/health").json() == {
        "status": "unavailable",
        "database": "unavailable",
    }


def test_cors_allows_configured_frontend(client):
    response = client.options(
        "/api/products",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    denied = client.get(
        "/api/products", headers={"Origin": "https://untrusted.example"}
    )
    assert "access-control-allow-origin" not in denied.headers


def test_sqlalchemy_columns_match_django_schema():
    inspector = inspect(engine)
    for table in Base.metadata.sorted_tables:
        actual = {column["name"] for column in inspector.get_columns(table.name)}
        assert {column.name for column in table.columns} == actual


def test_alembic_autogenerate_is_blocked():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "revision",
            "--autogenerate",
            "-m",
            "must-not-create",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Store tables are Django-owned" in result.stderr
