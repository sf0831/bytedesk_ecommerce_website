# ByteDesk

A portfolio store for computer and workspace equipment. All seven planned phases are complete: database and administration, public API, React storefront, authentication, shopping and checkout, reviews, and final quality checks.

## Architecture

```text
React/Vite -> FastAPI -> PostgreSQL <- Django Admin
```

Django owns schema migrations for the shared store tables. SQLAlchemy maps existing catalog, user, cart, wishlist, order and review tables. Alembic tracks a no-op API baseline in `api_alembic_version` and has autogeneration disabled; it does not create or alter Django-owned tables. Never run SQLAlchemy `create_all` against the store database. New shared schema changes must originate in Django migrations. Django exposes only `/admin/`, with no duplicate public API.

The frontend uses React, Vite, JavaScript, React Router and plain CSS. The backend uses FastAPI, Pydantic 2, SQLAlchemy 2, Alembic, Django 5.2, psycopg 3, PostgreSQL 16 and Docker Compose. Django's development server and bind mount are intended for local development, not a production deployment.

## Structure

```text
frontend/
  src/
    api/                     Fetch client and catalog, account, shopping and review requests
    components/              Navigation, cards, filters, pagination and states
    pages/                   Home, catalog, details, accounts, shopping, checkout, orders and 404
    hooks/                   Abortable API loading
    locales/                 English and Turkish interface messages
  public/images/             Local product photos and original equipment illustrations
  scripts/smoke.mjs           Route/proxy HTTP checks
backend/
  app/
    api/                     Thin catalog, account, shopping, review and health routes
    models/                  SQLAlchemy shared table mappings
    schemas/                 Pydantic query and response models
    services/                Catalog, authentication, cart, checkout and review logic
    config.py / database.py  Environment configuration and sessions
  alembic/                   API baseline; no shared table ownership
  tests/                     PostgreSQL-backed pytest tests
django_admin/
  config/                    Settings, URLs, WSGI and local test settings
  store/
    models.py                Shared schema
    admin.py                 Administration
    catalog.py               Local sample catalog
    migrations/              Django-owned migrations
    management/commands/     Idempotent seed command
    tests.py                 Schema, seed and Admin checks
docker/
  init-env.py                 Generate local development secrets
  verify-phase1.sh            Database/Admin verification
  verify-phase2.sh            Catalog API verification
  verify-phase3.sh            Storefront build and HTTP verification
  verify.sh                   Complete automated verification
.env.example
docker-compose.yml
```

## Run locally

Requires Python 3, Docker Engine, the Compose plugin and permission to access the Docker daemon.

```sh
python3 docker/init-env.py
docker compose up -d --build
docker compose exec django python manage.py seed_store
```

Startup waits for PostgreSQL health and runs migrations before Django starts. FastAPI starts after Django is healthy, applies its Alembic baseline, and verifies the shared product table before serving requests. PostgreSQL data lives in the `postgres_data` Docker volume, outside the repository. PostgreSQL has no published host port; Django connects using the `postgres` service name. Admin is bound to the loopback interface at [http://localhost:8000/admin/](http://localhost:8000/admin/). The API is bound to [http://localhost:8001](http://localhost:8001), with [Swagger UI](http://localhost:8001/docs) and [ReDoc](http://localhost:8001/redoc). Inside Compose the API connects to `postgres:5432`; host ports are separate from container service addresses.

The storefront runs at [http://localhost:5173/](http://localhost:5173/). Vite proxies `/api` requests to `http://fastapi:8000` inside Compose, so no Docker hostname is sent to the browser. The four development services are `postgres`, `django`, `fastapi` and `frontend`.

Login uses `ADMIN_USERNAME` and `ADMIN_PASSWORD` from your generated `.env`. The seed command creates an administrator only if that username does not exist; it never resets an existing password or elevates an existing account. Treat the generated credentials as local development credentials.

```sh
docker compose logs -f django
docker compose exec django python manage.py migrate
docker compose down
```

`docker compose down` preserves data. `docker compose down -v` **deletes the database volume**.

## Environment

`.env.example` contains placeholders, not working credentials. The helper generates random values into an ignored `.env`; do not commit it.

| Variable | Purpose |
| --- | --- |
| APP_ENV | `development` permits sample seeding; other values enforce production checks |
| POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD | Database and credentials |
| POSTGRES_HOST / POSTGRES_PORT | `postgres` / `5432` inside Compose |
| DJANGO_SECRET_KEY | Required random application secret |
| DJANGO_DEBUG | `true` for local Admin static assets; `false` outside development |
| DJANGO_ALLOWED_HOSTS | Comma-separated allowed hosts |
| ADMIN_USERNAME / ADMIN_EMAIL / ADMIN_PASSWORD | Development seed administrator |
| VITE_API_BASE_URL | Optional public browser API origin; blank uses the Vite `/api` proxy |
| CORS_ORIGINS | Comma-separated explicit frontend origins; defaults to localhost/127.0.0.1 on port 5173 |
| JWT_SECRET_KEY / JWT_ALGORITHM / ACCESS_TOKEN_EXPIRE_MINUTES | Required signing secret, HS256 algorithm and session expiry |

Non-development settings reject debug mode, short Django secrets, and placeholder database passwords. Production hosting, HTTPS and static asset serving require a separate deployment configuration; this Compose setup is for development.

## Database design

All 13 requested entities are implemented. Users use Django's custom `AbstractUser` with hashed passwords and case-insensitive unique email. Taxonomies protect referenced products. Product SKU and slug are unique. Prices and inventory cannot be negative.

```text
User -> Cart -> CartItem -> Product <- Category / Brand
User -> Wishlist -> WishlistItem -> Product
User -> Order -> OrderItem -> Product (nullable)
User -> Review -> Product -> Images / Specifications
```

Each user has at most one cart and wishlist. Item pairs and user/product review pairs are unique. Quantities must be positive and ratings range from 1 to 5. Specifications are flexible key/value pairs, unique per product and key.

Order items preserve product name, unit price, quantity and subtotal. Product deletion sets their product reference to NULL and preserves snapshots. Users referenced by orders cannot be deleted. Order totals and item subtotals have database checks. Foreign keys and uniqueness provide ordinary indexes; extra indexes cover active products by price and customer orders by date. FastAPI checkout locks inventory rows and creates orders transactionally, with a retry key to prevent duplicate orders.

Django deletion behavior is enforced by its ORM collector. SQLAlchemy exposes no customer product/user deletion service; any future deletion service must honor these rules too; raw PostgreSQL deletes are constrained by foreign keys and do not run Django's deletion collector.

## Administration

Products support search, category/brand/active filters, sortable columns, editable inventory and active flags, and image/specification inlines. Images accept local paths or URLs; no external scraping or image service is used. Seed products include local copies of web-sourced product photos; the home page uses the same photos in its featured product grid while retaining the hero/category artwork. Admin can supply product-specific images.

Orders show customers, amounts, dates and read-only item snapshots. Only status is editable, and Admin does not allow order creation or deletion. Review approval defaults to false and can be changed from the review list. User, cart, wishlist, brand and category management are included.

## Seed data

```sh
docker compose exec django python manage.py seed_store
```

Creates five categories, four brands and 20 sample products, including an out-of-stock product, flexible specifications and product photos. Names are realistic; sample prices and specifications are illustrative. Existing product values, specifications, images and passwords are preserved. Products without any image receive a sample photo on seeding; existing image collections are never overwritten. The whole seed runs in one transaction, and it refuses to run outside development.

## Verification and tests

Run the complete PostgreSQL/container workflow:

```sh
./docker/verify-phase1.sh
```

It builds and starts containers, checks database health, migration drift, applied migrations, seeding twice, tests against PostgreSQL and Admin HTTP access.

Or run the database tests directly:

```sh
docker compose exec django python manage.py test store --verbosity=2
```

The development PostgreSQL user can create Django's temporary test database. Tests exercise database constraints, hashed credentials, protected relationships, preserved order history, seed idempotency and authenticated Admin pages. The optional `config.test_settings` uses in-memory SQLite for quick local checks; it does not replace PostgreSQL verification.

## FastAPI catalog

All Phase 2 endpoints are public and read-only:

| Method | Path | Result |
| --- | --- | --- |
| GET | `/api/health` | Database readiness (`200` or `503`) |
| GET | `/api/products` | Paginated active product catalog |
| GET | `/api/products/{slug}` | Product detail, images, specifications and stock |
| GET | `/api/categories` | Categories, sorted by name |
| GET | `/api/categories/{slug}` | One category |
| GET | `/api/brands` | Brands, sorted by name |
| GET | `/api/brands/{slug}` | One brand |

```sh
curl 'http://localhost:8001/api/products?search=keyboard&category=keyboards&brand=keychron&min_price=50&max_price=200&sort=price_asc&page=1&page_size=20'
curl 'http://localhost:8001/api/products/keychron-k2-wireless-keyboard'
curl 'http://localhost:8001/api/categories'
```

Search matches name, SKU, description, category and brand case-insensitively. Search `%` and `_` are literal characters, not wildcards. Category and brand filters take exact slugs; price bounds are inclusive. Sorting accepts `name_asc` (default), `name_desc`, `price_asc`, `price_desc` and `newest`, with an ID tie-breaker for stable pagination. Page numbers start at 1, page size defaults to 20 and is capped at 100. Pagination beyond the end returns an empty list. A product list response includes `items`, `total`, `page`, `page_size` and `total_pages`.

Amounts serialize as decimal strings to preserve exact money values. Each product includes nested category/brand, images, stock quantity and `in_stock`. Inactive products are hidden from listings and return 404 on detail access. Out-of-stock active products remain visible. Invalid filters return 422; missing resources return 404; database failures return a safe 503 message. Catalog relationships are eagerly loaded to avoid per-product queries.

### Phase 2 verification

```sh
./docker/verify-phase2.sh
# Or run PostgreSQL-backed integration tests directly:
docker compose exec -T fastapi pytest -q -p no:cacheprovider
```

The development image installs `requirements-dev.txt`; the ordinary `backend/Dockerfile` installs runtime dependencies only. Tests require the existing Django-migrated PostgreSQL database and `APP_ENV=development`. They add uniquely named fixture rows inside a transaction and roll them back after each test, preserving the development catalog. No SQLite replacement schema is used for API integration tests.

To inspect the independent API baseline:

```sh
docker compose exec fastapi alembic current
docker compose exec fastapi alembic upgrade head
```

Alembic autogeneration is deliberately blocked. The no-op baseline and its tracking table coexist with `django_migrations`; Django remains the owner of all shared store tables. Authentication, carts, checkout and reviews use the same API and shared database, as described below.


## React storefront (Phase 3)

Implemented routes: `/`, `/products`, `/products/:slug`, plus a friendly unmatched-route page. The shared navbar, category links and footer use API taxonomies. Products, prices, stock, images and specifications come from FastAPI; no product catalog is hard-coded in React.

The catalog supports search, category/brand filters, an applied price range, sorting and pagination (12 products per page). State lives in query parameters and survives direct links, refreshes and browser history. Requests are aborted when views change, so older responses cannot replace a newer search. Loading, empty, validation, missing-product and retry states are included.

On narrow screens, navigation becomes a disclosure menu with search, catalog filters become a collapsible panel, the grid becomes two columns and product detail sections stack. Desktop and tablet layouts retain visible search and adapt the grids. Keyboard focus styles, input labels, a skip link and status announcements are included.

Catalog/search cards use local product photos sourced from manufacturer and retailer pages. Source links are recorded in `docs/product-image-sources.md`. The home page uses the same photos in featured product cards while retaining its original hero/category illustrations. Photos are served locally, so browsing does not contact an external image provider; illustrations remain available as a fallback. Product detail uses configured API images when present, supports a thumbnail gallery and falls back to a category illustration when images are missing or fail.

```sh
./docker/verify-phase3.sh
# Individual checks:
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run format:check
docker compose exec -T frontend npm run build
docker compose exec -T frontend npm run smoke
```

The smoke command checks the live Vite routes, SPA fallback and API proxy. Browser checks cover interactive filters, pagination, details and responsive layouts; the HTTP smoke check is not a browser test.

For development outside Docker, use Node 22.12+ (the container uses Node 22):

```sh
cd frontend
npm ci
npm run dev
```

With FastAPI running on host port 8001, Vite's local default proxy is `http://localhost:8001`. Set `API_PROXY_TARGET` to override the development proxy. `VITE_API_BASE_URL` is optional for a separately hosted API; it is public frontend configuration, never a place for secrets. A production static host must route unknown page paths to `index.html` and configure an API reverse proxy or set `VITE_API_BASE_URL` at build time. Vite's dev/preview servers are not a production hosting configuration.

Shopping and sign-in controls are integrated with the catalog and product detail pages.

## Authentication (Phase 4)

The public authentication API is FastAPI. Django remains the administration system and owns migration `store.0002_user_auth_version`. Both use the same users and Django-compatible PBKDF2-SHA256 hashes. FastAPI uses Django's password hasher utility without exposing a Django public API.

- `POST /api/auth/register`: JSON `username`, `email`, `password` (10–128 characters), optional `first_name` and `last_name`. Returns HTTP 201 with a JWT and a safe user profile. Usernames use 3–150 letters, numbers, or `. @ + - _`. Unknown fields, including administrative flags, are rejected.
- `POST /api/auth/login`: JSON `email`, `password`. Email matching is case insensitive; failed credentials use the same message for unknown, inactive and incorrect-password accounts.
- `GET /api/users/me`: requires `Authorization: Bearer <access_token>`.
- `POST /api/auth/logout`: requires the bearer token. Atomically increments the user's session version, invalidating all existing access tokens for that account. New login remains available.

JWTs use HS256, configured expiry, issuer and audience validation. Set a random `JWT_SECRET_KEY` of at least 32 characters. Missing, short and example-placeholder secrets fail startup. `python docker/init-env.py` generates secrets on a fresh checkout; it never overwrites an existing `.env`. Existing installations must fill their JWT secret and recreate FastAPI to load it.

React provides `/register`, `/login`, and protected `/profile` routes. It keeps the access token in per-tab `sessionStorage`, survives reloads, and clears it on logout or rejected authentication. No passwords are persisted by the application. The server validates restored sessions and the client checks active sessions on window focus and every minute. Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 30); login is required again, with no refresh-token implementation. JavaScript storage is accessible to same-origin scripts, so production deployment requires HTTPS and strong XSS protections. This phase does not include password reset, email verification, throttling or social login.

Use the **Authorize** button in `/docs` with the returned bearer token to try `/api/users/me` and logout. Public catalog routes continue to work without authentication. Registration creates regular customers, never admin users.

## Shopping and checkout (Phase 5)

All shopping routes require a bearer token. The frontend provides `/cart`, `/wishlist`, `/checkout`, `/orders` and `/orders/:id`. Sign-in returns to the requested protected page. The cart lives in PostgreSQL, persists across browser sessions, and is isolated per customer. Product pages provide quantity selection, add-to-cart and wishlist actions; the header shows the current cart quantity. Checkout accepts shipping information and creates a **demo order without collecting payment**.

```text
GET    /api/cart
POST   /api/cart/items                           {product_id, quantity}
PATCH  /api/cart/items/{item_id}                 {quantity}
DELETE /api/cart/items/{item_id}
GET    /api/wishlist
POST   /api/wishlist/items                       {product_id}
DELETE /api/wishlist/items/{product_id}
POST   /api/wishlist/items/{product_id}/move-to-cart
GET    /api/orders?page=1&page_size=20
GET    /api/orders/{id}
POST   /api/orders
```

Adding an existing cart product increases its quantity rather than adding a duplicate row. Quantity updates use the cart item ID; wishlist actions use product IDs. Wishlist additions are idempotent, including out-of-stock active products. Moving an unavailable product fails without removing it from the wishlist. Quantities must be integers from 1 through 10000, within available inventory. Cart additions do not reserve stock; checkout validates stock again. Products that become inactive remain removable from a customer's cart/wishlist but cannot be ordered.

The server calculates all prices and totals using `Decimal` and database product values. Shipping is **$8 below $100**, **free at $100 or more**, and **$0 for an empty cart**. No tax, shipping-provider or payment integration is implemented. Checkout rejects client-supplied prices, totals, user IDs and order statuses.

Example checkout JSON:

```json
{
  "checkout_key": "4e9d59d8-ef03-4a4c-b6a3-5e573053a78b",
  "shipping_name": "Demo Customer",
  "shipping_address": "42 Demo Street",
  "shipping_city": "Portland",
  "shipping_postal_code": "97201",
  "shipping_country": "United States"
}
```

Generate a fresh UUID4 `checkout_key` for each checkout attempt and reuse it when retrying that attempt. The frontend generates one per mounted checkout form. The server stores it with a customer-specific uniqueness constraint; repeating it returns the original order without reducing stock or clearing newly added cart items. Existing installations must run Django migration `store.0003_order_checkout_key_order_unique_order_checkout_key` (the Compose Django startup command runs migrations). No extra infrastructure or idempotency table is needed.

Checkout obtains a customer row lock, then locks every requested product row in ascending ID order using PostgreSQL `SELECT ... FOR UPDATE`. Validation, order/item creation, inventory decrement and cart clearing happen in one transaction. Every API cart/wishlist mutation uses the same customer lock to serialize changes to that customer's containers. Competing customers cannot buy the same last unit; all failures roll back the transaction. These guarantees apply to mutations through the public API; arbitrary direct database writes and manual admin cart edits must not be used to simulate concurrent customer requests.

Order items store name, price, quantity and subtotal snapshots. Django's existing `SET_NULL` product deletion behavior preserves order history; orders protect their customer reference. Customers can read only their own orders; another customer's ID returns 404. Order lists paginate newest first. Django Admin displays the customer, shipping information, immutable totals and items, and can change status. Cancellation is an administrative status in this demo; it does not trigger an automatic inventory return or refund.

Run `docker compose exec fastapi pytest -q` for all API integration tests. Besides savepoint-based behavior tests, checkout concurrency tests use separate PostgreSQL connections and committed disposable fixtures, then remove only their own fixtures. Run tests against the development database (`APP_ENV=development`), never a production database. The existing Django tests also verify that snapshots survive product deletion.

## Reviews and moderation (Phase 6)

```text
GET  /api/reviews?product_id=10&page=1&page_size=10  Public approved reviews and rating summary
POST /api/reviews                                   Authenticated submission
GET  /api/reviews/me?product_id=10                   Authenticated customer's own review or null
```

Submit JSON `product_id`, integer `rating` from 1–5, `title` (3–160 characters) and `body` (10–5000 characters). Text is trimmed and validated; blank text, non-integer ratings and extra fields such as `user_id` or `is_approved` are rejected. Reviews are attributed to the authenticated customer and always start pending approval. The database's existing `unique_user_product_review` constraint enforces one review per customer/product, including pending reviews; duplicate submissions return 409. No new migration is needed for this phase.

Product detail pages show the approved review count, average rating rounded to one decimal, individual ratings/titles/bodies/dates and pagination. No ratings produces a null average and a clear empty state. Public author labels use the customer's first name or “ByteDesk customer”, never email addresses or account IDs. The author can privately see their own pending review and its moderation status; another customer cannot retrieve it through `/api/reviews/me`.

In Django Admin, open **Store → Reviews**, search by product/title/customer, filter by rating or approval, and toggle **Is approved** to publish/unpublish. Public listing and averages immediately follow the current approval state after refresh. The React submission form reports that approval is pending and suppresses another form when an existing review is found. Authenticated users can review any active product; this phase does not impose a purchase requirement or claim reviews are verified purchases.

Tests cover pending visibility, approval/unapproval, rating aggregates across all approved reviews (not just a page), pagination, duplicate review enforcement, request validation, private ownership, inactive/missing products and authentication. Existing Django Admin and review constraint tests continue to run.


## Final quality checks (Phase 7)

Run all automated checks with one command after generating `.env`:

```sh
./docker/verify.sh
```

This builds and waits for all services, checks migrations, runs the seed twice, checks Django, runs Django tests against PostgreSQL, runs API lint/formatting and PostgreSQL integration tests, and runs frontend lint/formatting, request-error tests, build and HTTP smoke checks. Browser interaction and responsive checks are separate from the HTTP smoke script. Test fixtures are isolated and cleaned up; your seeded catalog is preserved. The frontend build creates ignored `frontend/dist`; remove it when keeping a source-only checkout.

For frontend request handling tests alone:

```sh
docker compose exec -T frontend npm test
```

### Troubleshooting

- **Docker connection fails:** start Docker Engine and ensure your user can access its daemon.
- **Required environment variable missing:** run `python3 docker/init-env.py` on a fresh checkout. Existing `.env` files are preserved; compare their variable names with `.env.example` and fill any missing values.
- **Empty catalog:** run `docker compose exec django python manage.py seed_store`.
- **Service unhealthy:** inspect `docker compose logs django fastapi frontend` and `docker compose ps`. Changing environment variables requires recreating the affected service with `docker compose up -d`.
- **Port already in use:** free ports 8000, 8001 or 5173, or change their host mappings and the corresponding browser/CORS configuration.
- **Expired session:** sign in again. Logging out revokes all sessions for that customer.
- **Pending review:** approve it in Django Admin; refresh the product page.

### Portfolio scope

All requested phases are complete. No payment is collected, shipping is a fixed demo rule, and cancellation only changes status. The home page retains local hero/category artwork and uses product photos in featured cards; catalog photos are local copies of web-sourced product assets. The development servers and Compose settings are not a public production deployment. Deployment, payment integrations, password reset, email verification, abuse throttling and inventory returns on cancellation are optional future work; they are not additional phases of this project.

## English and Turkish

Use the **English / Türkçe** selector above the navigation. The storefront remembers the selection in browser storage (`bytedesk.language`), uses the browser language on the first visit, and updates the HTML `lang` attribute and page title. Product photos appear on the home page as well as the catalog and detail pages.

Interface messages live in `frontend/src/locales/en.json` and `tr.json`, using i18next and react-i18next. Translate complete messages with named interpolation values; use `_one` / `_other` messages for counts. Prices use `Intl.NumberFormat` and dates use the active locale (`en-US` / `tr-TR`). **All prices remain USD**; switching languages does not convert currency. Product and brand names, SKUs, slugs, customer addresses, reviews and historical order snapshots remain as entered.

Django Admin owns editable Turkish catalog fields: category `name_tr`, product `description_tr`, image `alt_text_tr`, and specification `key_tr` / `value_tr`. Blank translations fall back to English. The seed command fills missing sample translations without replacing administrator edits. The new fields are added by Django migrations, not Alembic.

The product list/detail and category endpoints accept `?lang=en` or `?lang=tr` (default English). Search covers both English and Turkish category names and product descriptions. Business errors return an English `detail`, a stable `code`, and safe `params`; React translates by code rather than matching English sentences. Request validation uses the frontend's standard translated validation message.

To update an existing checkout:

```sh
docker compose up -d --build --wait
docker compose exec django python manage.py seed_store
```

The frontend refreshes its dependency volume with `npm ci` on startup so a changed lockfile is applied. Run `docker compose exec frontend npm test` for translation key/interpolation parity, referenced keys, plurals, fallback and API-client checks. The complete `docker/verify.sh` workflow also checks catalog localization against PostgreSQL and seed preservation through Django tests.
