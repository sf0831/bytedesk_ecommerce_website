from sqlalchemy import select

from app.models import ProductSpecification


def test_turkish_catalog_and_english_remain_separate(client, db, catalog):
    product = catalog["products"][0]
    category = catalog["category"]
    category.name_tr = "Deneme Klavyeler"
    product.description_tr = "Sessiz çalışma alanları için mekanik klavye."
    spec = db.scalar(
        select(ProductSpecification).where(
            ProductSpecification.product_id == product.id
        )
    )
    spec.key_tr = "Düzen"
    spec.value_tr = "%75"
    db.flush()
    tr = client.get(f"/api/products/{product.slug}?lang=tr").json()
    assert tr["description"] == product.description_tr
    assert tr["category"]["name"] == category.name_tr
    assert tr["specifications"][0]["key"] == "Düzen"
    assert tr["specifications"][0]["value"] == "%75"
    en = client.get(f"/api/products/{product.slug}").json()
    assert en["description"] == product.description
    assert en["category"]["name"] == category.name
    assert en["specifications"][0]["key"] == "Layout"
    assert (tr["id"], tr["slug"], tr["sku"], tr["price"]) == (
        en["id"],
        en["slug"],
        en["sku"],
        en["price"],
    )
    assert (
        client.get(f"/api/categories/{category.slug}?lang=tr").json()["name"]
        == category.name_tr
    )
    assert any(
        c["name"] == category.name_tr
        for c in client.get("/api/categories?lang=tr").json()
    )
    result = client.get(
        "/api/products", params={"category": category.slug, "lang": "tr"}
    ).json()
    assert all(p["category"]["name"] == category.name_tr for p in result["items"])


def test_empty_translation_falls_back_to_english(client, catalog):
    product = catalog["products"][0]
    en = client.get(f"/api/products/{product.slug}?lang=en").json()
    tr = client.get(f"/api/products/{product.slug}?lang=tr").json()
    assert tr == en


def test_search_in_turkish_content(client, db, catalog):
    product = catalog["products"][0]
    product.description_tr = "benzersiz-yerelleştirme-denemesi"
    db.flush()
    response = client.get(
        "/api/products", params={"search": "yerelleştirme", "lang": "tr"}
    )
    assert [p["id"] for p in response.json()["items"]] == [product.id]


def test_invalid_language_is_rejected(client):
    for path in [
        "/api/products",
        "/api/products/example",
        "/api/categories",
        "/api/categories/example",
    ]:
        assert client.get(path, params={"lang": "invalid"}).status_code == 422


def test_stable_error_codes_preserve_details_and_auth_header(client):
    missing = client.get("/api/products/missing-localization-product")
    assert missing.status_code == 404
    assert missing.json() == {
        "detail": "Product not found",
        "code": "product_not_found",
        "params": {},
    }
    denied = client.post(
        "/api/auth/login",
        json={"email": "no-user@example.com", "password": "wrong-password"},
    )
    assert denied.status_code == 401
    assert denied.json()["code"] == "invalid_credentials"
    assert denied.headers["www-authenticate"] == "Bearer"
