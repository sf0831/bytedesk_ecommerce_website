from fastapi import APIRouter

from ..dependencies import CurrentUser, DatabaseSession
from ..schemas.cart import AddCartItem, CartResponse, SetQuantity
from ..services import cart

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.get("", response_model=CartResponse)
def read(db: DatabaseSession, user: CurrentUser):
    return cart.read_cart(db, user.id)


@router.post("/items", response_model=CartResponse)
def add(data: AddCartItem, db: DatabaseSession, user: CurrentUser):
    return cart.add(db, user.id, data.product_id, data.quantity)


@router.patch("/items/{item_id}", response_model=CartResponse)
def update(item_id: int, data: SetQuantity, db: DatabaseSession, user: CurrentUser):
    return cart.change(db, user.id, item_id, data.quantity)


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove(item_id: int, db: DatabaseSession, user: CurrentUser):
    return cart.change(db, user.id, item_id, None)
