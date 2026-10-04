from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from ..models import Product, Wishlist, WishlistItem
from ..schemas.wishlist import WishlistLine, WishlistResponse
from . import cart
from .errors import StoreError


def read_wishlist(db: Session, user_id: int) -> WishlistResponse:
    wishlist = db.scalar(select(Wishlist).where(Wishlist.user_id == user_id))
    if wishlist is None:
        return WishlistResponse(items=[])
    lines = db.scalars(
        select(WishlistItem)
        .where(WishlistItem.wishlist_id == wishlist.id)
        .order_by(WishlistItem.id)
        .options(selectinload(WishlistItem.product).options(*cart.product_options()))
    )
    return WishlistResponse(
        items=[
            WishlistLine(
                product=line.product,
                available=line.product.is_active and line.product.stock_quantity > 0,
            )
            for line in lines
        ]
    )


def add(db: Session, user_id: int, product_id: int) -> WishlistResponse:
    try:
        cart.lock_customer(db, user_id)
        product = db.get(Product, product_id)
        if product is None or not product.is_active:
            raise StoreError(404, "Product not found.", code="product_not_found")
        wishlist = cart.container(db, Wishlist, user_id)
        exists = db.scalar(
            select(WishlistItem.id).where(
                WishlistItem.wishlist_id == wishlist.id,
                WishlistItem.product_id == product_id,
            )
        )
        if exists is None:
            db.add(WishlistItem(wishlist_id=wishlist.id, product_id=product_id))
            wishlist.updated_at = datetime.now(timezone.utc)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return read_wishlist(db, user_id)


def change(db: Session, user_id: int, product_id: int, move: bool = False):
    try:
        cart.lock_customer(db, user_id)
        line = db.scalar(
            select(WishlistItem)
            .join(Wishlist)
            .where(Wishlist.user_id == user_id, WishlistItem.product_id == product_id)
        )
        if line is None:
            raise StoreError(
                404, "Wishlist item not found.", code="wishlist_item_not_found"
            )
        if move:
            cart.add_item(db, user_id, product_id)
        wishlist = db.get(Wishlist, line.wishlist_id)
        wishlist.updated_at = datetime.now(timezone.utc)
        db.execute(delete(WishlistItem).where(WishlistItem.id == line.id))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return cart.read_cart(db, user_id) if move else read_wishlist(db, user_id)
