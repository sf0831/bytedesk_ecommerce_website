from fastapi import APIRouter

from ..dependencies import CurrentUser, DatabaseSession
from ..schemas.cart import CartResponse, ProductSelection
from ..schemas.wishlist import WishlistResponse
from ..services import wishlist

router = APIRouter(prefix="/api/wishlist", tags=["Wishlist"])


@router.get("", response_model=WishlistResponse)
def read(db: DatabaseSession, user: CurrentUser):
    return wishlist.read_wishlist(db, user.id)


@router.post("/items", response_model=WishlistResponse)
def add(data: ProductSelection, db: DatabaseSession, user: CurrentUser):
    return wishlist.add(db, user.id, data.product_id)


@router.delete("/items/{product_id}", response_model=WishlistResponse)
def remove(product_id: int, db: DatabaseSession, user: CurrentUser):
    return wishlist.change(db, user.id, product_id)


@router.post("/items/{product_id}/move-to-cart", response_model=CartResponse)
def move(product_id: int, db: DatabaseSession, user: CurrentUser):
    return wishlist.change(db, user.id, product_id, move=True)
