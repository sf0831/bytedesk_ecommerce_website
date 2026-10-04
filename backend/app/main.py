import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .api import (
    auth,
    brands,
    cart,
    categories,
    health,
    orders,
    products,
    reviews,
    users,
    wishlist,
)
from .config import get_settings
from .database import SessionLocal, engine
from .models import Product
from .schemas.common import ErrorResponse
from .services.errors import StoreError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail startup if the database or Django-owned catalog schema is unavailable.
    with SessionLocal() as db:
        db.execute(select(Product.id).limit(1))
    yield
    engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="ByteDesk API",
        version="1.0.0",
        description="Storefront API for catalog, accounts, shopping, orders and reviews. Shared schema and administration are managed by Django.",
        lifespan=lifespan,
        responses={
            503: {
                "model": ErrorResponse,
                "description": "Database temporarily unavailable",
            }
        },
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().allowed_origins,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )
    for router in (
        health.router,
        products.router,
        categories.router,
        brands.router,
        auth.router,
        users.router,
        cart.router,
        wishlist.router,
        orders.router,
        reviews.router,
    ):
        app.include_router(router)

    @app.exception_handler(StoreError)
    async def store_error(request: Request, exc: StoreError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.code, "params": exc.params},
            headers=exc.headers,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request: Request, exc: SQLAlchemyError):
        logger.exception("Store database operation failed", exc_info=exc)
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Store temporarily unavailable. Please try again.",
                "code": "store_unavailable",
                "params": {},
            },
        )

    return app


app = create_app()
